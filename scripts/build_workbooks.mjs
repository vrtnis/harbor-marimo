import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = process.cwd();
const out = path.join(root, "demo_data");

const palette = {
  navy: "#132238",
  teal: "#0F766E",
  aqua: "#DDF4EF",
  blue: "#2F6BFF",
  green: "#008000",
  ink: "#172033",
  muted: "#64748B",
  line: "#D9E1EA",
  soft: "#F5F7FA",
  actual: "#EEF2F7",
  forecast: "#E7F6F2",
  warning: "#FFF4D8",
  white: "#FFFFFF",
};

const amountFormat = '$#,##0.0;[Red]($#,##0.0);-';
const percentFormat = '0.0%;[Red](0.0%);-';

function setColumnWidths(sheet) {
  sheet.getRange("A:A").format.columnWidth = 26;
  sheet.getRange("B:H").format.columnWidth = 13;
  sheet.getRange("I:I").format.columnWidth = 3;
  sheet.getRange("J:M").format.columnWidth = 17;
}

function titleBand(sheet, range, title, subtitle) {
  sheet.getRange(range).merge();
  sheet.getRange(range).values = [[title]];
  sheet.getRange(range).format = {
    fill: palette.navy,
    font: { bold: true, color: palette.white, size: 18 },
    verticalAlignment: "center",
  };
  sheet.getRange("A3:H3").merge();
  sheet.getRange("A3:H3").values = [[subtitle]];
  sheet.getRange("A3:H3").format = {
    fill: palette.soft,
    font: { color: palette.muted, size: 10 },
    verticalAlignment: "center",
  };
  sheet.getRange("A1:H2").format.rowHeight = 25;
  sheet.getRange("A3:H3").format.rowHeight = 21;
}

function styleHeader(range, fill = palette.teal) {
  range.format = {
    fill,
    font: { bold: true, color: palette.white },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    borders: { preset: "all", style: "thin", color: palette.line },
  };
}

function styleBody(range) {
  range.format = {
    font: { color: palette.ink },
    borders: { preset: "all", style: "thin", color: palette.line },
    verticalAlignment: "center",
  };
}

async function buildModel(filePath, variant) {
  const workbook = Workbook.create();
  const summary = workbook.worksheets.add("Summary");
  const assumptions = workbook.worksheets.add("Assumptions");
  const forecast = workbook.worksheets.add("Forecast");
  const checks = workbook.worksheets.add("Checks");

  for (const sheet of [summary, assumptions, forecast, checks]) {
    sheet.showGridLines = false;
    setColumnWidths(sheet);
  }

  titleBand(
    assumptions,
    "A1:H2",
    "Northstar Software — Forecast Assumptions",
    "Illustrative data • $ millions • FY23–FY29"
  );
  assumptions.getRange("A5:H5").values = [[
    "Driver",
    "FY23A",
    "FY24A",
    "FY25A",
    "FY26E",
    "FY27E",
    "FY28E",
    "FY29E",
  ]];
  styleHeader(assumptions.getRange("A5:H5"));

  const updated = variant === "formula-preserved";
  const fy27Growth = updated ? 200 / 190 - 1 : 0.05;
  const fy27Margin = updated ? 0.52 : 0.51;
  assumptions.getRange("A6:H11").values = [
    ["Revenue growth", null, 0.1, 180 / 165 - 1, 190 / 180 - 1, fy27Growth, 0.08, 0.08],
    ["Gross margin", 0.49, 0.5, 0.51, 0.515, fy27Margin, 0.525, 0.53],
    ["", null, null, null, null, null, null, null],
    ["R&D expense", 14, 15, 16, 17, 18, 19, 20],
    ["Sales & marketing", 18, 19, 21, 23, 25, 27, 29],
    ["G&A expense", 11, 11.5, 12, 13, 13.8, 14.5, 15.2],
  ];
  styleBody(assumptions.getRange("A6:H11"));
  assumptions.getRange("B6:H7").format.numberFormat = percentFormat;
  assumptions.getRange("B9:H11").format.numberFormat = amountFormat;
  assumptions.getRange("B6:H11").format.font = { color: palette.blue };
  assumptions.getRange("F6:F7").format.fill = palette.warning;
  assumptions.getRange("A13:H15").merge(true);
  assumptions.getRange("A13:H15").values = [
    ["Blue font = editable assumptions. Yellow cells are the FY27 assumptions referenced in the task."],
    ["Source: synthetic case-study data created for this integration demo."],
    ["The example is illustrative and does not represent a real company or investment view."],
  ];
  assumptions.getRange("A13:H15").format = {
    fill: palette.soft,
    font: { color: palette.muted, size: 9 },
    wrapText: true,
  };
  assumptions.freezePanes.freezeRows(5);

  titleBand(
    forecast,
    "A1:H2",
    "Northstar Software — Operating Forecast",
    "Illustrative data • $ millions • Green links reference the Assumptions sheet"
  );
  forecast.getRange("A4:H4").values = [[
    "Metric",
    "FY23A",
    "FY24A",
    "FY25A",
    "FY26E",
    "FY27E",
    "FY28E",
    "FY29E",
  ]];
  styleHeader(forecast.getRange("A4:D4"), palette.navy);
  styleHeader(forecast.getRange("E4:H4"), palette.teal);
  forecast.getRange("A5:A17").values = [
    ["Revenue"],
    ["Growth"],
    [""],
    ["Gross profit"],
    ["Gross margin"],
    [""],
    ["Operating expenses"],
    ["R&D"],
    ["Sales & marketing"],
    ["G&A"],
    [""],
    ["EBITDA"],
    ["EBITDA margin"],
  ];
  forecast.getRange("B5:D5").values = [[150, 165, 180]];
  forecast.getRange("B6:D6").values = [[null, 0.1, 180 / 165 - 1]];
  forecast.getRange("B8:D8").values = [[73.5, 82.5, 91.8]];
  forecast.getRange("B9:D9").values = [[0.49, 0.5, 0.51]];
  forecast.getRange("B12:D14").values = [
    [14, 15, 16],
    [18, 19, 21],
    [11, 11.5, 12],
  ];
  forecast.getRange("B16").formulas = [["=B8-SUM(B12:B14)"]];
  forecast.getRange("B16:D16").fillRight();
  forecast.getRange("B17").formulas = [["=B16/B5"]];
  forecast.getRange("B17:D17").fillRight();
  forecast.getRange("E5").formulas = [["=D5*(1+Assumptions!E6)"]];
  forecast.getRange("F5").formulas = [["=E5*(1+Assumptions!F6)"]];
  forecast.getRange("G5").formulas = [["=F5*(1+Assumptions!G6)"]];
  forecast.getRange("H5").formulas = [["=G5*(1+Assumptions!H6)"]];
  forecast.getRange("E6").formulas = [["=E5/D5-1"]];
  forecast.getRange("E6:H6").fillRight();
  forecast.getRange("E8").formulas = [["=E5*Assumptions!E7"]];
  forecast.getRange("F8").formulas = [["=F5*Assumptions!F7"]];
  forecast.getRange("G8").formulas = [["=G5*Assumptions!G7"]];
  forecast.getRange("H8").formulas = [["=H5*Assumptions!H7"]];
  forecast.getRange("E9").formulas = [["=E8/E5"]];
  forecast.getRange("E9:H9").fillRight();
  forecast.getRange("E12").formulas = [["=Assumptions!E9"]];
  forecast.getRange("F12").formulas = [["=Assumptions!F9"]];
  forecast.getRange("G12").formulas = [["=Assumptions!G9"]];
  forecast.getRange("H12").formulas = [["=Assumptions!H9"]];
  forecast.getRange("E13").formulas = [["=Assumptions!E10"]];
  forecast.getRange("F13").formulas = [["=Assumptions!F10"]];
  forecast.getRange("G13").formulas = [["=Assumptions!G10"]];
  forecast.getRange("H13").formulas = [["=Assumptions!H10"]];
  forecast.getRange("E14").formulas = [["=Assumptions!E11"]];
  forecast.getRange("F14").formulas = [["=Assumptions!F11"]];
  forecast.getRange("G14").formulas = [["=Assumptions!G11"]];
  forecast.getRange("H14").formulas = [["=Assumptions!H11"]];
  forecast.getRange("E16").formulas = [["=E8-SUM(E12:E14)"]];
  forecast.getRange("E16:H16").fillRight();
  forecast.getRange("E17").formulas = [["=E16/E5"]];
  forecast.getRange("E17:H17").fillRight();

  if (variant === "hardcoded") {
    forecast.getRange("F16").values = [[47.2]];
    forecast.getRange("F16").format.font = { color: palette.blue, bold: true };
    forecast.getRange("F16").format.fill = palette.warning;
  }

  styleBody(forecast.getRange("A5:H17"));
  forecast.getRange("B5:H5").format.numberFormat = amountFormat;
  forecast.getRange("B6:H6").format.numberFormat = percentFormat;
  forecast.getRange("B8:H8").format.numberFormat = amountFormat;
  forecast.getRange("B9:H9").format.numberFormat = percentFormat;
  forecast.getRange("B12:H16").format.numberFormat = amountFormat;
  forecast.getRange("B17:H17").format.numberFormat = percentFormat;
  forecast.getRange("B5:D14").format.font = { color: palette.blue };
  forecast.getRange("E5:H14").format.font = { color: palette.green };
  forecast.getRange("B16:E17").format.font = { color: palette.ink };
  forecast.getRange("G16:H17").format.font = { color: palette.ink };
  forecast.getRange("A5:H6").format.fill = palette.actual;
  forecast.getRange("E5:H17").format.fill = palette.forecast;
  forecast.getRange("A8:H9").format.fill = palette.soft;
  forecast.getRange("A16:H17").format = {
    fill: palette.aqua,
    font: { bold: true, color: palette.ink },
    borders: { preset: "doubleBottom", style: "thin", color: palette.teal },
  };
  if (variant === "hardcoded") {
    forecast.getRange("F16").format = {
      fill: palette.warning,
      font: { color: palette.blue, bold: true },
      borders: { preset: "all", style: "medium", color: "#E9A23B" },
      numberFormat: amountFormat,
    };
  }
  forecast.freezePanes.freezeRows(4);

  titleBand(
    checks,
    "A1:H2",
    "Model Checks",
    "The baseline verifier checks output values; it does not assess every structural property."
  );
  checks.getRange("A5:D5").values = [["Check", "Actual", "Expected", "Status"]];
  styleHeader(checks.getRange("A5:D5"));
  checks.getRange("A6:A8").values = [
    ["FY27 EBITDA"],
    ["FY27 revenue"],
    ["Workbook calculation"],
  ];
  checks.getRange("B6").formulas = [["=Forecast!F16"]];
  checks.getRange("C6").values = [[47.2]];
  checks.getRange("D6").formulas = [["=IF(ABS(B6-C6)<0.01,\"PASS\",\"FAIL\")"]];
  checks.getRange("B7").formulas = [["=Forecast!F5"]];
  checks.getRange("C7").values = [[200]];
  checks.getRange("D7").formulas = [["=IF(ABS(B7-C7)<0.01,\"PASS\",\"FAIL\")"]];
  checks.getRange("B8").formulas = [["=COUNT(Forecast!B5:H17)"]];
  checks.getRange("C8").values = [[1]];
  checks.getRange("D8").formulas = [["=IF(B8>0,\"PASS\",\"FAIL\")"]];
  styleBody(checks.getRange("A6:D8"));
  checks.getRange("B6:C7").format.numberFormat = amountFormat;
  checks.getRange("B6:B8").format.font = { color: palette.green };
  checks.getRange("C6:C8").format.font = { color: palette.blue };
  checks.getRange("A10:H12").merge(true);
  checks.getRange("A10:H12").values = [
    ["Why this matters"],
    ["A task-specific marimo view can place the verifier outcome beside the artifact and the recorded trajectory."],
    ["This workbook is only one example of the broader Harbor → marimo integration pattern."],
  ];
  checks.getRange("A10:H10").format = {
    fill: palette.navy,
    font: { bold: true, color: palette.white },
  };
  checks.getRange("A11:H12").format = {
    fill: palette.soft,
    font: { color: palette.muted },
    wrapText: true,
  };

  titleBand(
    summary,
    "A1:H2",
    "Northstar Software — Forecast Summary",
    "Illustrative artifact used in the Acto × Harbor × marimo integration demo"
  );
  summary.getRange("A5:B5").merge();
  summary.getRange("D5:E5").merge();
  summary.getRange("G5:H5").merge();
  summary.getRange("A6:B8").merge();
  summary.getRange("D6:E8").merge();
  summary.getRange("G6:H8").merge();
  summary.getRange("A5:B5").values = [["FY27 Revenue"]];
  summary.getRange("D5:E5").values = [["FY27 EBITDA"]];
  summary.getRange("G5:H5").values = [["EBITDA Margin"]];
  for (const range of ["A5:B5", "D5:E5", "G5:H5"]) {
    summary.getRange(range).format = {
      fill: palette.teal,
      font: { bold: true, color: palette.white },
      horizontalAlignment: "center",
    };
  }
  summary.getRange("A6").formulas = [["=Forecast!F5"]];
  summary.getRange("D6").formulas = [["=Forecast!F16"]];
  summary.getRange("G6").formulas = [["=Forecast!F17"]];
  summary.getRange("A6:B8").format = {
    fill: palette.aqua,
    font: { bold: true, color: palette.green, size: 20 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    numberFormat: amountFormat,
    borders: { preset: "outside", style: "thin", color: palette.line },
  };
  summary.getRange("D6:E8").format = {
    fill: palette.aqua,
    font: { bold: true, color: palette.green, size: 20 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    numberFormat: amountFormat,
    borders: { preset: "outside", style: "thin", color: palette.line },
  };
  summary.getRange("G6:H8").format = {
    fill: palette.aqua,
    font: { bold: true, color: palette.green, size: 20 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    numberFormat: percentFormat,
    borders: { preset: "outside", style: "thin", color: palette.line },
  };
  summary.getRange("A11:C18").values = [
    ["Period", "Revenue", "EBITDA"],
    ["FY23A", 150, 30.5],
    ["FY24A", 165, 37],
    ["FY25A", 180, 42.8],
    ["FY26E", 190, 44.85],
    ["FY27E", variant === "formula-preserved" ? 200 : 199.5, variant === "hardcoded" ? 47.2 : variant === "formula-preserved" ? 47.2 : 44.945],
    ["FY28E", variant === "formula-preserved" ? 216 : 215.46, variant === "formula-preserved" ? 52.9 : 52.63],
    ["FY29E", variant === "formula-preserved" ? 233.28 : 232.697, variant === "formula-preserved" ? 59.44 : 59.129],
  ];
  styleBody(summary.getRange("A11:C18"));
  styleHeader(summary.getRange("A11:C11"));
  summary.getRange("B12:C18").format.numberFormat = amountFormat;
  const chart = summary.charts.add("line", summary.getRange("A11:C18"));
  chart.title = "Revenue and EBITDA Trend";
  chart.hasLegend = true;
  chart.xAxis = { axisType: "textAxis" };
  chart.yAxis = { numberFormatCode: "$#,##0" };
  chart.setPosition("E11", "M27");
  summary.getRange("A21:H23").merge(true);
  summary.getRange("A21:H23").values = [
    ["Demo note"],
    ["This is a synthetic workbook used to make Harbor's artifact handoff visible. The case study is about the integration pattern, not the finance example."],
    ["Open the Forecast sheet to inspect the underlying formulas and assumptions."],
  ];
  summary.getRange("A21:H21").format = {
    fill: palette.navy,
    font: { bold: true, color: palette.white },
  };
  summary.getRange("A22:H23").format = {
    fill: palette.soft,
    font: { color: palette.muted },
    wrapText: true,
  };

  const formulaErrors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 100 },
    summary: `formula error scan: ${variant}`,
  });
  console.log(formulaErrors.ndjson);

  const exported = await SpreadsheetFile.exportXlsx(workbook);
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await exported.save(filePath);
  return workbook;
}

await buildModel(path.join(out, "task", "forecast_input.xlsx"), "baseline");
await buildModel(
  path.join(out, "harbor_job", "forecast-update__trial-017", "artifacts", "workspace", "forecast.xlsx"),
  "hardcoded"
);
const goodWorkbook = await buildModel(
  path.join(out, "harbor_job", "forecast-update__trial-018", "artifacts", "workspace", "forecast.xlsx"),
  "formula-preserved"
);
const exampleWorkbook = await SpreadsheetFile.exportXlsx(goodWorkbook);
await exampleWorkbook.save(path.join(root, "outputs", "demo", "forecast-example.xlsx"));
await buildModel(
  path.join(out, "harbor_job", "forecast-update__trial-019", "artifacts", "workspace", "forecast.xlsx"),
  "baseline"
);

for (const sheetName of ["Summary", "Assumptions", "Forecast", "Checks"]) {
  const preview = await goodWorkbook.render({
    sheetName,
    autoCrop: "all",
    scale: 1,
    format: "png",
  });
  const bytes = new Uint8Array(await preview.arrayBuffer());
  await fs.writeFile(path.join(root, "outputs", "demo", `${sheetName.toLowerCase()}.png`), bytes);
}

const badWorkbookFile = await SpreadsheetFile.importXlsx(
  await (await import("@oai/artifact-tool")).FileBlob.load(
    path.join(out, "harbor_job", "forecast-update__trial-017", "artifacts", "workspace", "forecast.xlsx")
  )
);
const badPreview = await badWorkbookFile.render({
  sheetName: "Forecast",
  range: "A1:H17",
  scale: 1.4,
  format: "png",
});
await fs.writeFile(
  path.join(root, "outputs", "demo", "forecast-hardcoded.png"),
  new Uint8Array(await badPreview.arrayBuffer())
);

console.log("Workbook fixtures built and rendered.");
