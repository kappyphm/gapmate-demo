import { DATA_SAMPLES } from "./data";
import { DESIGN_SAMPLES } from "./design";
import { EDGE_SAMPLES } from "./edge";
import { FINANCE_SAMPLES } from "./finance";
import { HR_SAMPLES } from "./hr";
import { IT_SAMPLES } from "./it";
import { LOGISTICS_SAMPLES } from "./logistics";
import { MARKETING_SAMPLES } from "./marketing";
import { PM_SAMPLES } from "./pm";
import { SALES_SAMPLES } from "./sales";
import type { SamplePair } from "./types";

export type { SamplePair } from "./types";

export const SAMPLES: SamplePair[] = [
  ...IT_SAMPLES,
  ...MARKETING_SAMPLES,
  ...SALES_SAMPLES,
  ...FINANCE_SAMPLES,
  ...HR_SAMPLES,
  ...DESIGN_SAMPLES,
  ...DATA_SAMPLES,
  ...LOGISTICS_SAMPLES,
  ...PM_SAMPLES,
  ...EDGE_SAMPLES,
];

export interface SampleGroup {
  industry: string;
  samples: SamplePair[];
}

export const SAMPLE_GROUPS: SampleGroup[] = [
  { industry: "IT", samples: IT_SAMPLES },
  { industry: "Marketing", samples: MARKETING_SAMPLES },
  { industry: "Sales", samples: SALES_SAMPLES },
  { industry: "Finance", samples: FINANCE_SAMPLES },
  { industry: "HR", samples: HR_SAMPLES },
  { industry: "Design", samples: DESIGN_SAMPLES },
  { industry: "Data", samples: DATA_SAMPLES },
  { industry: "Logistics", samples: LOGISTICS_SAMPLES },
  { industry: "PM", samples: PM_SAMPLES },
  { industry: "Edge cases", samples: EDGE_SAMPLES },
];

export const DEFAULT_SAMPLE: SamplePair = SAMPLES[0];

export const SAMPLE_CV = DEFAULT_SAMPLE.cv;
export const SAMPLE_JD = DEFAULT_SAMPLE.jd;
