/**
 * Shared slide vocabulary for the E-O-D project finance decks.
 * Consumed by model/build_pptx.js. Every figure comes from model/pf_model.json.
 */
const CR = 100.0;

// Brand palette, carried across from the HTML decks. Validated for categorical
// chart use (lightness, chroma, CVD separation) — the green sits below 3:1 against
// a light surface, so every chart carries visible data labels as the relief.
const C = {
  ink:      "0A1426",
  inkSoft:  "3B4660",
  inkMute:  "6E7689",
  white:    "FFFFFF",
  paper:    "F5F6F8",
  rule:     "E2E4EA",
  blue:     "2B66EA",
  blueDeep: "2A51A3",
  terra:    "C8553D",
  green:    "10B981",
  amber:    "D97706",
};
const SERIES = [C.blue, C.terra, C.green, C.amber];

const F = { head: "Calibri", body: "Calibri" };
const W = 13.333, H = 7.5, M = 0.62;              // LAYOUT_WIDE, margins

// Build-time overflow reporting: a panel that cannot fit the space left on its
// slide is recorded here rather than silently clipped.
const OVERFLOWS = [];
const CURRENT = { deck: "", slide: 0 };
function mark(deck, slide) { CURRENT.deck = deck; CURRENT.slide = slide; }
function overflowReport() { return OVERFLOWS; }

// ---------------------------------------------------------------- formatting --
const cr  = (x, d = 2) => x == null ? "—" : `₹${(x / CR).toFixed(d)} Cr`;
const crN = (x, d = 2) => x == null ? "—" : (x / CR).toFixed(d);
const lk  = (x, d = 1) => x == null ? "—" : `₹${x.toFixed(d)} L`;
const pc  = (x, d = 1) => x == null ? "—" : `${x.toFixed(d)}%`;
const pp  = (x, d = 1) => x == null ? "—" : `${x >= 0 ? "+" : ""}${x.toFixed(d)} pp`;
const xx  = (x, d = 2) => x == null ? "—" : `${x.toFixed(d)}×`;
const money = x => x == null ? "—"
  : Math.abs(x) < 100 ? `₹${(+x.toFixed(1)).toString().replace(/\.0$/, "")} lakh`
                      : `₹${(+(x / CR).toFixed(2)).toString().replace(/\.00$/, "")} crore`;

// ---------------------------------------------------------------- measuring --
/**
 * Estimated rendered height, in inches, of `text` in a box `w` inches wide.
 * Calibri averages ~0.47em per character; the 1.06 factor is slack so a panel
 * is never sized shorter than the text it has to hold.
 */
function measure(text, w, fontSize, lineSpacingPt) {
  const ls = lineSpacingPt || fontSize * 1.36;
  const charsPerLine = Math.max(8, Math.floor((w * 72) / (fontSize * 0.47)));
  let lines = 0;
  for (const para of String(text).split("\n")) {
    lines += para.length === 0 ? 1 : Math.ceil(para.length / charsPerLine);
  }
  return (lines * ls / 72) * 1.04;
}

// ------------------------------------------------------------------- slides ---
/** Dark cover with a stat strip. */
function cover(s, { eyebrow, title, sub, meta, stats }) {
  s.background = { color: C.ink };
  s.addText(eyebrow.toUpperCase(), {
    x: M, y: 0.62, w: 8.2, h: 0.3, fontFace: F.head, fontSize: 12, bold: true,
    color: C.terra, charSpacing: 2.4, margin: 0,
  });
  s.addText(title, {
    x: M, y: 1.05, w: 9.4, h: 1.85, fontFace: F.head, fontSize: 50, bold: true,
    color: C.white, lineSpacing: 52, margin: 0, valign: "top",
  });
  const subW = 11.2, subH = measure(sub, subW, 15, 23);
  s.addText(sub, {
    x: M, y: 2.96, w: subW, h: subH, fontFace: F.body, fontSize: 15, italic: true,
    color: "C9D0DE", lineSpacing: 23, margin: 0, valign: "top",
  });
  s.addText(meta, {
    x: M, y: 2.96 + subH + 0.16, w: subW, h: 0.76, fontFace: F.body, fontSize: 11.5,
    color: "8A93A6", lineSpacing: 18, margin: 0, valign: "top",
  });
  s.addShape("rect", { x: M, y: 5.12, w: W - 2 * M, h: 0.012, fill: { color: "2A3247" } });
  const n = stats.length, gap = 0.28;
  const cw = (W - 2 * M - gap * (n - 1)) / n;
  stats.forEach((t, i) => {
    const x = M + i * (cw + gap);
    s.addText(t.label.toUpperCase(), {
      x, y: 5.36, w: cw, h: 0.26, fontFace: F.body, fontSize: 9.5, bold: true,
      color: "8A93A6", charSpacing: 1.4, margin: 0,
    });
    s.addText(t.value, {
      x, y: 5.63, w: cw, h: 0.56, fontFace: F.head, fontSize: 29, bold: true,
      color: C.white, margin: 0, valign: "top",
    });
    if (t.sub) s.addText(t.sub, {
      x, y: 6.2, w: cw, h: 0.62, fontFace: F.body, fontSize: 10,
      color: "A8B2C4", lineSpacing: 13.5, margin: 0, valign: "top",
    });
  });
}

/** Light content slide: numbered chip, title, optional lede. Returns the y to build from. */
function head(s, n, title, lede) {
  s.background = { color: C.white };
  s.addShape("ellipse", { x: M, y: 0.5, w: 0.42, h: 0.42, fill: { color: C.blue } });
  s.addText(n, {
    x: M, y: 0.5, w: 0.42, h: 0.42, fontFace: F.head, fontSize: 13, bold: true,
    color: C.white, align: "center", valign: "middle", margin: 0,
  });
  s.addText(title, {
    x: M + 0.62, y: 0.44, w: W - 2 * M - 0.62, h: 0.56, fontFace: F.head,
    fontSize: 30, bold: true, color: C.ink, margin: 0, valign: "middle",
  });
  if (lede) {
    const ledeH = measure(lede, W - 2 * M, 12.5, 17.5);
    s.addText(lede, {
      x: M, y: 1.04, w: W - 2 * M, h: ledeH, fontFace: F.body, fontSize: 12.5,
      color: C.inkSoft, lineSpacing: 17.5, margin: 0, valign: "top",
    });
    return 1.04 + ledeH + 0.14;
  }
  return 1.24;
}

/** Row of large stat callouts on a tinted card. */
function stats(s, y, cells, opts = {}) {
  const n = cells.length, gap = 0.24;
  const cw = (W - 2 * M - gap * (n - 1)) / n;
  const h = opts.h || 1.42;
  cells.forEach((t, i) => {
    const x = M + i * (cw + gap);
    s.addShape("roundRect", {
      x, y, w: cw, h, rectRadius: 0.06,
      fill: { color: t.tint || C.paper },
      line: { color: t.line || C.rule, width: 1 },
    });
    s.addText(t.label.toUpperCase(), {
      x: x + 0.2, y: y + 0.13, w: cw - 0.4, h: 0.26, fontFace: F.body, fontSize: 8.5,
      bold: true, color: C.inkMute, charSpacing: 1.0, margin: 0, valign: "top",
    });
    let vpt = t.small ? 20 : 26;
    while (measure(t.value, cw - 0.4, vpt, vpt * 1.1) > 0.44 && vpt > 12) vpt -= 1;
    s.addText(t.value, {
      x: x + 0.2, y: y + 0.4, w: cw - 0.4, h: 0.5, fontFace: F.head,
      fontSize: vpt, bold: true, color: t.color || C.ink,
      margin: 0, valign: "top", fit: "shrink",
    });
    if (t.sub) s.addText(t.sub, {
      x: x + 0.2, y: y + 0.92, w: cw - 0.4, h: h - 1.0, fontFace: F.body,
      fontSize: 9.5, color: C.inkMute, lineSpacing: 12.5, margin: 0, valign: "top",
    });
  });
  return y + h + 0.26;
}

/** Data table. rows: array of arrays; first column left, rest right-aligned. */
function table(s, y, headers, rows, opts = {}) {
  const colW = opts.colW || [4.4, ...Array(headers.length - 1).fill(
    (W - 2 * M - 4.4) / (headers.length - 1))];
  const body = [[...headers.map((h, i) => ({
    text: h,
    options: {
      bold: true, fontSize: 9.5, color: C.inkMute, fill: { color: C.white },
      align: i === 0 ? "left" : "right", valign: "bottom", charSpacing: 1,
      border: [{ pt: 0 }, { pt: 0 }, { pt: 1.4, color: C.ink }, { pt: 0 }],
      margin: [2, 6, 5, 0],
    },
  }))]];
  rows.forEach(r => {
    const em = r.emphasis;
    body.push(r.cells.map((c, i) => {
      const o = typeof c === "object" ? c : { text: c };
      return {
        text: o.text,
        options: {
          fontSize: opts.fontSize || 11, bold: em === "total" || i === 0 && em,
          color: o.color || (em === "total" ? C.ink : C.inkSoft),
          fill: { color: em === "total" ? "FBF1EE" : em === "sub" ? "F2F6FE" : C.white },
          align: i === 0 ? "left" : "right", valign: "middle",
          border: [{ pt: 0 }, { pt: 0 }, { pt: 0.6, color: C.rule }, { pt: 0 }],
          margin: [5, 6, 5, 0],
        },
      };
    }));
  });
  const rowH = opts.rowH || 0.3, fs = opts.fontSize || 11;
  s.addTable(body, {
    x: M, y, w: W - 2 * M, colW, fontFace: F.body, rowH, autoPage: false,
  });
  // Actual height: a row grows past rowH when its text wraps, so measure each one.
  let hh = rowH;                                     // header
  rows.forEach(r => {
    let tall = rowH;
    r.cells.forEach((c, i) => {
      const t = typeof c === "object" ? c.text : c;
      const plain = String(t).replace(/<[^>]+>/g, "");
      tall = Math.max(tall, measure(plain, colW[i] - 0.18, fs, fs * 1.25) + 0.14);
    });
    hh += tall;
  });
  // Same guard the callout panels get: a table that runs past the footer line is
  // clipped in the rendered deck, so fail the build rather than ship it.
  const roomT = H - 0.54 - y;
  if (hh > roomT + 0.02) {
    OVERFLOWS.push({ slide: CURRENT.slide, deck: CURRENT.deck,
                     headline: `table: ${String(headers[0] || "").slice(0, 40) || headers.length + " cols"}`,
                     need: +hh.toFixed(2), room: +roomT.toFixed(2),
                     short: +(hh - roomT).toFixed(2) });
  }
  return y + hh + 0.18;
}

/** Coloured conclusion panel. kind: go | caution | stop | note */
function verdict(s, y, kind, headline, bodyText, h) {
  const K = {
    go:      { bg: "EDFAF4", line: C.green, tag: C.green },
    caution: { bg: "FDF6EC", line: C.amber, tag: C.amber },
    stop:    { bg: "FBEFEC", line: C.terra, tag: C.terra },
    note:    { bg: "F1F5FE", line: C.blue,  tag: C.blueDeep },
  }[kind];
  const innerW = W - 2 * M - 0.52;
  // shrink the body a step at a time until the panel fits the space left on the slide
  const room = H - 0.54 - y;                       // keep clear of the footer
  let bodyPt = 12, headPt = 19, hh;
  for (;;) {
    const headH = measure(headline, innerW, headPt, headPt * 1.15);
    hh = 0.34 + headH + 0.08 + measure(bodyText, innerW, bodyPt, bodyPt * 1.42) + 0.18;
    if (hh <= room || bodyPt <= 9) break;
    bodyPt -= 0.5;
    if (bodyPt < 11.5 && headPt > 14) headPt -= 1;
  }
  if (h && h > hh) hh = h;                          // caller may reserve more
  if (hh > room) {                                  // genuinely over-full slide
    OVERFLOWS.push({ slide: CURRENT.slide, deck: CURRENT.deck,
                     headline: headline.slice(0, 54), need: +hh.toFixed(2),
                     room: +room.toFixed(2), short: +(hh - room).toFixed(2) });
    hh = Math.max(0.8, room);
  }
  const headH = measure(headline, innerW, headPt, headPt * 1.15);
  s.addShape("roundRect", {
    x: M, y, w: W - 2 * M, h: hh, rectRadius: 0.05,
    fill: { color: K.bg }, line: { color: K.line, width: 1.25 },
  });
  s.addText(kind === "note" ? "NOTE" : "VERDICT", {
    x: M + 0.26, y: y + 0.12, w: 3, h: 0.2, fontFace: F.body, fontSize: 8.5,
    bold: true, color: K.tag, charSpacing: 1.6, margin: 0,
  });
  s.addText(headline, {
    x: M + 0.26, y: y + 0.32, w: innerW, h: headH, fontFace: F.head,
    fontSize: headPt, bold: true, color: C.ink, margin: 0, valign: "top",
    lineSpacing: headPt * 1.15,
  });
  s.addText(bodyText, {
    x: M + 0.26, y: y + 0.32 + headH + 0.06, w: innerW,
    h: Math.max(0.2, hh - 0.4 - headH - 0.06), fontFace: F.body,
    fontSize: bodyPt, color: C.inkSoft, lineSpacing: bodyPt * 1.42,
    margin: 0, valign: "top",
  });
  return y + hh + 0.22;
}

/** Three financing options side by side. */
function optionCards(s, y, cards, h) {
  const gap = 0.26, cw = (W - 2 * M - gap * 2) / 3, hh = h || 3.5;
  cards.forEach((c, i) => {
    const x = M + i * (cw + gap);
    const pick = !!c.pick;
    s.addShape("roundRect", {
      x, y, w: cw, h: hh, rectRadius: 0.06,
      fill: { color: pick ? "EDFAF4" : C.white },
      line: { color: pick ? C.green : C.rule, width: pick ? 1.5 : 1 },
    });
    s.addText(c.tag.toUpperCase(), {
      x: x + 0.22, y: y + 0.18, w: cw - 0.44, h: 0.22, fontFace: F.body,
      fontSize: 8.5, bold: true, color: pick ? C.green : C.inkMute,
      charSpacing: 1.4, margin: 0,
    });
    s.addText(c.name, {
      x: x + 0.22, y: y + 0.42, w: cw - 0.44, h: 0.3, fontFace: F.head,
      fontSize: 15, bold: true, color: C.ink, margin: 0, valign: "top",
    });
    s.addText(c.big, {
      x: x + 0.22, y: y + 0.78, w: cw - 0.44, h: 0.52, fontFace: F.head,
      fontSize: c.bigSmall ? 20 : 30, bold: true, color: c.bigColor || C.ink,
      margin: 0, valign: "top",
    });
    s.addText(c.cap.toUpperCase(), {
      x: x + 0.22, y: y + 1.32, w: cw - 0.44, h: 0.24, fontFace: F.body,
      fontSize: 8.5, bold: true, color: C.inkMute, charSpacing: 1.1, margin: 0,
    });
    c.rows.forEach((r, j) => {
      const ry = y + 1.66 + j * 0.36;
      s.addShape("rect", { x: x + 0.22, y: ry, w: cw - 0.44, h: 0.008,
                           fill: { color: C.rule } });
      s.addText(r[0], {
        x: x + 0.22, y: ry + 0.05, w: (cw - 0.44) * 0.56, h: 0.28,
        fontFace: F.body, fontSize: 9.5, color: C.inkMute, margin: 0, valign: "middle",
      });
      s.addText(r[1], {
        x: x + 0.22 + (cw - 0.44) * 0.56, y: ry + 0.05, w: (cw - 0.44) * 0.44, h: 0.28,
        fontFace: F.body, fontSize: 9.5, bold: true, color: C.ink,
        align: "right", margin: 0, valign: "middle",
      });
    });
  });
  return y + hh + 0.22;
}

/** Bulleted risk / item list in two columns. */
function itemList(s, y, items, opts = {}) {
  const cols = opts.cols || 2, gap = 0.4;
  const cw = (W - 2 * M - gap * (cols - 1)) / cols;
  const per = Math.ceil(items.length / cols);
  items.forEach((it, i) => {
    const col = Math.floor(i / per), row = i % per;
    const x = M + col * (cw + gap);
    const iy = y + row * (opts.rowH || 0.94);
    s.addShape("ellipse", { x, y: iy + 0.04, w: 0.2, h: 0.2,
                            fill: { color: it.color || C.blue } });
    s.addText(it.title, {
      x: x + 0.32, y: iy, w: cw - 0.32, h: 0.26, fontFace: F.head, fontSize: 12.5,
      bold: true, color: C.ink, margin: 0, valign: "middle",
    });
    s.addText(it.body, {
      x: x + 0.32, y: iy + 0.27, w: cw - 0.32, h: (opts.rowH || 0.94) - 0.32,
      fontFace: F.body, fontSize: 10.5, color: C.inkSoft, lineSpacing: 14,
      margin: 0, valign: "top",
    });
  });
  return y + per * (opts.rowH || 0.94);
}

/** Native chart with the house frame. Data labels are always on (palette relief). */
function chart(s, pres, y, type, data, opts = {}) {
  const stacked = type === "barStacked";
  const ct = pres.ChartType[stacked ? "bar" : type];
  if (!ct) throw new Error(`unknown chart type "${type}"`);
  s.addChart(ct, data, Object.assign({
    barGrouping: stacked ? "stacked" : "clustered",
    x: opts.x != null ? opts.x : M,
    y, w: opts.w || (W - 2 * M), h: opts.h || 3.2,
    chartColors: opts.colors || SERIES,
    showTitle: !!opts.title, title: opts.title, titleFontFace: F.head,
    titleFontSize: 12, titleColor: C.inkMute, titleAlign: "left",
    showLegend: data.length > 1, legendPos: "t", legendFontFace: F.body,
    legendFontSize: 10, legendColor: C.inkSoft,
    showValue: true, dataLabelFontFace: F.body, dataLabelFontSize: 9,
    dataLabelColor: C.inkSoft, dataLabelFormatCode: opts.fmt || "0.00",
    dataLabelPosition: opts.labelPos || (stacked ? "ctr" : type === "bar" ? "outEnd" : "t"),
    catAxisLabelFontFace: F.body, catAxisLabelFontSize: 10, catAxisLabelColor: C.inkSoft,
    valAxisLabelFontFace: F.body, valAxisLabelFontSize: 10, valAxisLabelColor: C.inkMute,
    valAxisTitle: opts.axisTitle, showValAxisTitle: !!opts.axisTitle,
    valAxisTitleFontFace: F.body, valAxisTitleFontSize: 10, valAxisTitleColor: C.inkMute,
    valGridLine: { color: C.rule, size: 1 }, catGridLine: { style: "none" },
    barGapWidthPct: opts.gap || 45, border: { pt: 0 },
    plotArea: { fill: { color: C.white } },
  }, opts.extra || {}));
  return y + (opts.h || 3.2) + 0.2;
}

/** Dark closing slide carrying the recommendation. */
function closing(s, { eyebrow, headline, body, steps }) {
  s.background = { color: C.ink };
  s.addText(eyebrow.toUpperCase(), {
    x: M, y: 0.6, w: 8, h: 0.28, fontFace: F.body, fontSize: 11, bold: true,
    color: C.green, charSpacing: 2.2, margin: 0,
  });
  s.addText(headline, {
    x: M, y: 0.98, w: W - 2 * M, h: 1.0, fontFace: F.head, fontSize: 34, bold: true,
    color: C.white, lineSpacing: 38, margin: 0, valign: "top",
  });
  s.addText(body, {
    x: M, y: 2.1, w: W - 2 * M, h: 1.5, fontFace: F.body, fontSize: 13.5,
    color: "C9D0DE", lineSpacing: 20, margin: 0, valign: "top",
  });
  if (steps) {
    const gap = 0.26, cw = (W - 2 * M - gap * (steps.length - 1)) / steps.length;
    steps.forEach((st, i) => {
      const x = M + i * (cw + gap);
      s.addShape("roundRect", { x, y: 3.85, w: cw, h: 2.6, rectRadius: 0.06,
                                fill: { color: "141D33" }, line: { color: "2A3247", width: 1 } });
      s.addShape("ellipse", { x: x + 0.22, y: 4.05, w: 0.4, h: 0.4, fill: { color: st.color || C.blue } });
      s.addText(String(i + 1), {
        x: x + 0.22, y: 4.05, w: 0.4, h: 0.4, fontFace: F.head, fontSize: 13, bold: true,
        color: C.white, align: "center", valign: "middle", margin: 0,
      });
      s.addText(st.title, {
        x: x + 0.22, y: 4.56, w: cw - 0.44, h: 0.52, fontFace: F.head, fontSize: 14,
        bold: true, color: C.white, margin: 0, valign: "top", lineSpacing: 18,
      });
      s.addText(st.body, {
        x: x + 0.22, y: 5.12, w: cw - 0.44, h: 1.2, fontFace: F.body, fontSize: 10.5,
        color: "9AA3B6", lineSpacing: 14, margin: 0, valign: "top",
      });
    });
  }
}

/** Footer stamp for content slides. */
function foot(s, text) {
  s.addText(text, {
    x: M, y: H - 0.46, w: W - 2 * M, h: 0.24, fontFace: F.body, fontSize: 8.5,
    color: C.inkMute, margin: 0, valign: "middle",
  });
}

module.exports = { mark, overflowReport, C, SERIES, F, W, H, M, CR, cr, crN, lk, pc, pp, xx, money, measure,
                   cover, head, stats, table, verdict, optionCards, itemList,
                   chart, closing, foot };
