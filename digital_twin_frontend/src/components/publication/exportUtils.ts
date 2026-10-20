export function saveFile(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function tableCSV(table: HTMLTableElement) {
  const rows = Array.from(table.rows);
  const excluded = new Set<number>();
  rows.forEach(row => Array.from(row.cells).forEach((cell, index) => {
    if (cell.querySelector('button, input, select') || /^(acciones|actions?)$/i.test(cell.textContent?.trim() || '')) excluded.add(index);
  }));
  return '\ufeff' + rows.map(row => Array.from(row.cells)
    .filter((_, index) => !excluded.has(index))
    .map(cell => {
      let value = cell.textContent?.trim() || '';
      if (/^[\s]*[=+\-@]/.test(value)) value = "'" + value;
      return '"' + value.replaceAll('"', '""') + '"';
    }).join(',')).join('\r\n');
}

export function scientificSVG(source: SVGSVGElement, width: number, description: string) {
  const clone = source.cloneNode(true) as SVGSVGElement;
  const originalNodes = [source, ...source.querySelectorAll('*')];
  const clonedNodes = [clone, ...clone.querySelectorAll('*')];
  originalNodes.forEach((element, i) => {
    const computed = getComputedStyle(element);
    for (const property of ['fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'opacity', 'font-size', 'font-family', 'font-weight', 'text-anchor']) {
      (clonedNodes[i] as SVGElement).style.setProperty(property, computed.getPropertyValue(property));
    }
  });
  const box = source.viewBox.baseVal;
  const printBox = { x: box.x - 85, y: box.y - 20, width: (box.width || source.clientWidth) + 110, height: (box.height || source.clientHeight) + 65 };
  const ratio = printBox.height / printBox.width;
  clone.setAttribute('viewBox', `${printBox.x} ${printBox.y} ${printBox.width} ${printBox.height}`);
  clone.style.width = '';
  clone.style.height = '';
  clone.style.maxWidth = '';
  clone.style.minWidth = '';
  clone.style.maxHeight = '';
  clone.style.minHeight = '';
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  clone.setAttribute('width', `${width}mm`);
  clone.setAttribute('height', `${width * ratio}mm`);
  clone.style.background = 'white';
  const background = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  background.setAttribute('x', String(printBox.x));
  background.setAttribute('y', String(printBox.y));
  background.setAttribute('width', String(printBox.width));
  background.setAttribute('height', String(printBox.height));
  background.setAttribute('fill', 'white');
  clone.prepend(background);
  // Keep text legible when exporting from the application's dark theme.
  clone.querySelectorAll('text').forEach(text => {
    text.style.fill = '#222';
    const minimum = 7 * printBox.width / (width / 25.4 * 72);
    text.style.fontSize = `${Math.max(parseFloat(text.style.fontSize) || 0, minimum)}px`;
  });
  const desc = document.createElementNS('http://www.w3.org/2000/svg', 'desc');
  desc.textContent = description;
  clone.prepend(desc);
  return { text: new XMLSerializer().serializeToString(clone), ratio };
}

// Add PNG physical resolution metadata so editors recognize 600 dpi.
export async function withPrintDPI(blob: Blob) {
  const png = new Uint8Array(await blob.arrayBuffer());
  const chunk = new Uint8Array(21);
  const view = new DataView(chunk.buffer);
  view.setUint32(0, 9);
  chunk.set([112, 72, 89, 115], 4); // pHYs
  view.setUint32(8, Math.round(600 / .0254));
  view.setUint32(12, Math.round(600 / .0254));
  chunk[16] = 1;
  let crc = 0xffffffff;
  for (const byte of chunk.subarray(4, 17)) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
  }
  view.setUint32(17, (crc ^ 0xffffffff) >>> 0);
  const parts: BlobPart[] = [png.slice(0, 8)];
  let offset = 8;
  while (offset + 12 <= png.length) {
    const length = new DataView(png.buffer, png.byteOffset + offset, 4).getUint32(0);
    const end = offset + 12 + length;
    if (end > png.length) throw new Error('PNG inválido.');
    const type = String.fromCharCode(...png.slice(offset + 4, offset + 8));
    if (type !== 'pHYs') parts.push(png.slice(offset, end));
    if (type === 'IHDR') parts.push(chunk);
    offset = end;
  }
  return new Blob(parts, { type: 'image/png' });
}

export async function exportPNG(svg: string, width: number, ratio: number) {
  const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
  try {
    const image = new Image();
    image.src = url;
    await image.decode();
    const canvas = document.createElement('canvas');
    canvas.width = Math.round(width / 25.4 * 600);
    canvas.height = Math.round(canvas.width * ratio);
    const context = canvas.getContext('2d');
    if (!context) throw new Error('No se pudo crear la imagen.');
    context.fillStyle = 'white';
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(image, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise<Blob>((resolve, reject) => canvas.toBlob(value => value ? resolve(value) : reject(new Error('Error al exportar PNG.')), 'image/png'));
    return await withPrintDPI(blob);
  } finally { URL.revokeObjectURL(url); }
}
