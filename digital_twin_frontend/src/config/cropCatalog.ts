export type CropSupportStatus =
  | "SUPPORTED"
  | "EXPERIMENTAL";

export interface CropCatalogItem {
  code: string;
  backendValue: string;
  labelEs: string;
  labelEn: string;
  scientificName?: string;
  supportStatus: CropSupportStatus;
  engineProfile: string | null;
}


export const CROP_CATALOG:
CropCatalogItem[] = [
  {
    code: "maize",
    backendValue: "Maize",
    labelEs: "Maíz",
    labelEn: "Maize",
    scientificName: "Zea mays",
    supportStatus: "SUPPORTED",
    engineProfile: "MAIZE",
  },
  {
    code: "potato",
    backendValue: "Potato",
    labelEs: "Papa",
    labelEn: "Potato",
    scientificName: "Solanum tuberosum",
    supportStatus: "EXPERIMENTAL",
    engineProfile: null,
  },
  {
    code: "rice",
    backendValue: "Rice",
    labelEs: "Arroz",
    labelEn: "Rice",
    scientificName: "Oryza sativa",
    supportStatus: "EXPERIMENTAL",
    engineProfile: null,
  },
  {
    code: "wheat",
    backendValue: "Wheat",
    labelEs: "Trigo",
    labelEn: "Wheat",
    scientificName: "Triticum aestivum",
    supportStatus: "EXPERIMENTAL",
    engineProfile: null,
  },
  {
    code: "onion",
    backendValue: "Onion",
    labelEs: "Cebolla",
    labelEn: "Onion",
    scientificName: "Allium cepa",
    supportStatus: "EXPERIMENTAL",
    engineProfile: null,
  },
  {
    code: "tomato",
    backendValue: "Tomato",
    labelEs: "Tomate",
    labelEn: "Tomato",
    scientificName: "Solanum lycopersicum",
    supportStatus: "EXPERIMENTAL",
    engineProfile: null,
  },
  {
    code: "avocado",
    backendValue: "Avocado",
    labelEs: "Palta",
    labelEn: "Avocado",
    scientificName: "Persea americana",
    supportStatus: "EXPERIMENTAL",
    engineProfile: null,
  },
  {
    code: "coffee",
    backendValue: "Coffee",
    labelEs: "Café",
    labelEn: "Coffee",
    scientificName: "Coffea spp.",
    supportStatus: "EXPERIMENTAL",
    engineProfile: null,
  },
  {
    code: "sugarcane",
    backendValue: "Sugarcane",
    labelEs: "Caña de azúcar",
    labelEn: "Sugarcane",
    scientificName: "Saccharum officinarum",
    supportStatus: "EXPERIMENTAL",
    engineProfile: null,
  },
  {
    code: "quinoa",
    backendValue: "Quinoa",
    labelEs: "Quinua",
    labelEn: "Quinoa",
    scientificName: "Chenopodium quinoa",
    supportStatus: "EXPERIMENTAL",
    engineProfile: null,
  },
];


const ALIASES:
Record<string, string> = {
  maize: "maize",
  corn: "maize",
  "maíz": "maize",
  maiz: "maize",
  potato: "potato",
  papa: "potato",
  rice: "rice",
  arroz: "rice",
  wheat: "wheat",
  trigo: "wheat",
  onion: "onion",
  cebolla: "onion",
  tomato: "tomato",
  tomate: "tomato",
  avocado: "avocado",
  palta: "avocado",
  coffee: "coffee",
  café: "coffee",
  cafe: "coffee",
  sugarcane: "sugarcane",
  "sugar cane": "sugarcane",
  "caña de azúcar": "sugarcane",
  "cana de azucar": "sugarcane",
  quinoa: "quinoa",
  quinua: "quinoa",
};


export function normalizeCropCode(
  value:
    | string
    | null
    | undefined
): string | null {

  if (!value) {
    return null;
  }

  const normalized =
    value
      .trim()
      .toLowerCase();

  return (
    ALIASES[normalized]
    ?? normalized
  );
}


export function getCropCatalogItem(
  value:
    | string
    | null
    | undefined
): CropCatalogItem | null {

  const code =
    normalizeCropCode(
      value
    );

  if (!code) {
    return null;
  }

  return (
    CROP_CATALOG.find(
      (crop) =>
        crop.code === code
        ||
        crop.backendValue
          .toLowerCase() ===
          value
            ?.trim()
            .toLowerCase()
    )
    ?? null
  );
}


export function getCropLabel(
  value:
    | string
    | null
    | undefined,
  locale:
    "es"
    | "en" = "es"
): string {

  const crop =
    getCropCatalogItem(
      value
    );

  if (!crop) {
    return (
      value?.trim()
      || "Cultivo no definido"
    );
  }

  return locale === "en"
    ? crop.labelEn
    : crop.labelEs;
}


export function getCropBackendValue(
  code: string
): string {

  return (
    CROP_CATALOG.find(
      (crop) =>
        crop.code === code
    )
    ?.backendValue
    ?? code
  );
}


export function getCropCodeFromValue(
  value:
    | string
    | null
    | undefined
): string {

  return (
    getCropCatalogItem(
      value
    )?.code
    ?? ""
  );
}


export function getCropSupportLabel(
  value:
    | string
    | null
    | undefined
): string {

  const crop =
    getCropCatalogItem(
      value
    );

  if (!crop) {
    return "Sin perfil agronómico";
  }

  return crop.supportStatus === "SUPPORTED"
    ? "Modelo agronómico disponible"
    : "Soporte experimental";
}
