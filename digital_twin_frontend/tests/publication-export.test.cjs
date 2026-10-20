const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');
const source = fs.readFileSync('src/components/publication/exportUtils.ts', 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText;
const exportsObject = {};
vm.runInNewContext(compiled, { exports: exportsObject, Blob, Uint8Array, DataView, setTimeout });
const cell = (textContent, control = false) => ({ textContent, querySelector: () => control });

test('CSV removes action columns consistently and escapes textual formulas', () => {
  const csv = exportsObject.tableCSV({ rows: [
    { cells: [cell('Nombre'), cell('Acciones')] },
    { cells: [cell('=formula'), cell('Editar', true)] },
    { cells: [cell('Pedro'), cell('')] },
  ] });
  assert.equal(csv, '\ufeff"Nombre"\r\n"\'=formula"\r\n"Pedro"');
});

test('PNG replaces existing resolution metadata with exactly one 600 dpi chunk', async () => {
  function chunk(type, bytes) {
    const result = new Uint8Array(bytes.length + 12);
    new DataView(result.buffer).setUint32(0, bytes.length);
    result.set([...type].map(c => c.charCodeAt(0)), 4);
    result.set(bytes, 8);
    return result;
  }
  const input = new Blob([new Uint8Array([137,80,78,71,13,10,26,10]), chunk('IHDR', new Uint8Array(13)), chunk('pHYs', new Uint8Array(9)), chunk('IDAT', new Uint8Array(0)), chunk('IEND', new Uint8Array(0))]);
  const result = new Uint8Array(await (await exportsObject.withPrintDPI(input)).arrayBuffer());
  const resolutions = [];
  let offset = 8;
  while (offset < result.length) {
    const view = new DataView(result.buffer, offset);
    const length = view.getUint32(0);
    if (String.fromCharCode(...result.slice(offset + 4, offset + 8)) === 'pHYs') {
      resolutions.push(view.getUint32(8));
      assert.equal(view.getUint32(8), view.getUint32(12));
      assert.equal(result[offset + 16], 1);
    }
    offset += length + 12;
  }
  assert.deepEqual(resolutions, [23622]);
});

test('SVG keeps requested physical width and minimum readable print fonts', () => {
  const node = () => ({
    attributes: {}, style: { width: '100%', maxWidth: '600px', setProperty(key, value) { this[key.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase())] = value; } },
    setAttribute(key, value) { this.attributes[key] = value; }, prepend() {},
  });
  const originalText = node();
  const clonedText = node();
  const clone = node();
  clone.querySelectorAll = () => [clonedText];
  const original = { ...node(), viewBox: { baseVal: { x: 0, y: 0, width: 820, height: 400 } }, clientWidth: 820, clientHeight: 400,
    querySelectorAll: () => [originalText], cloneNode: () => clone };
  const localExports = {};
  vm.runInNewContext(compiled, {
    exports: localExports, Blob, Uint8Array, DataView,
    document: { createElementNS: node },
    getComputedStyle: () => ({ getPropertyValue: key => key === 'font-size' ? '8px' : '' }),
    XMLSerializer: class { serializeToString() { return '<svg/>'; } },
  });
  localExports.scientificSVG(original, 85, 'Caption');
  assert.equal(clone.attributes.width, '85mm');
  assert.equal(clone.style.width, '');
  assert.equal(clone.style.maxWidth, '');
  const printViewWidth = Number(clone.attributes.viewBox.split(' ')[2]);
  assert.ok(parseFloat(clonedText.style.fontSize) * (85 / 25.4 * 72) / printViewWidth >= 6.999);
});
