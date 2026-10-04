// Read the full text of every Chronicling America page a search returns, and
// print each place a name appears. Run on demand in the built-in browser pane,
// never by run.sh; docs/web_access.md says why this route and not curl.
//
//   1. Open any page on https://www.loc.gov/ in the built-in browser (curl and
//      the Python fetchers are answered with Cloudflare's check; the pane passes).
//   2. Paste this file into the browser's javascript tool, then start a scan:
//        scan('Dwight Smith', '1870/1880', 'sn85025007', 'Dwight Smith', 40)
//      arguments: the search text, a date range, the paper's LCCN (Alexandria
//      Gazette sn85025007, Evening Star sn83045462), a regex for the name as the
//      OCR may misread it, and how many results to read. It runs in the
//      background; the tool times out at 45 seconds, so poll `log`:
//        JSON.stringify(log.<key>.hits)
//      A hit is [date, ~200 characters around the name], flagged **LABEL** when
//      "colored", "Negro" or "black" sits within that window.
//   3. savePdf('gazette18720520p3', '1872-05-20', 3) saves a page's scan to
//      ~/Downloads, which code/sources/cite.py then files with --copy.
//
// Two calls per page was the first design and drew a 503 after about 55 pages.
// The search result already names the page's text address, so a page costs one
// request to tile.loc.gov and the search costs one to loc.gov. A 503 or 429
// still means a pause of a few minutes; this script waits 30 seconds and moves on.

window.sleep = ms => new Promise(s => setTimeout(s, ms));
window.log = window.log || {};

// The page's text, from the address its search result carries.
window.tiletext = async (x) => {
  let u = x.word_coordinates_url || x.image_url[2];
  u = (Array.isArray(u) ? u[0] : u).replace(/#.*/, '').replace(/([?&])q=[^&]*&?/, '$1');
  if (!/full_text/.test(u)) u += (u.includes('?') ? '&' : '?') + 'full_text=1';
  const r = await fetch(u);
  if (r.status != 200) return { err: r.status };
  return { text: Object.values(await r.json())[0].full_text };
};

window.scan = async (q, dates, lccn, nameRe, max = 40, key = q.replace(/\W+/g, '_')) => {
  const L = window.log[key] = { read: 0, errs: 0, hits: [], total: 0, done: false };
  let d;
  for (let t = 0; t < 3 && !d; t++) {
    try {
      const r = await fetch(`https://www.loc.gov/collections/chronicling-america/?q=${encodeURIComponent(q)}`
        + `&dates=${dates}&fa=number_lccn:${lccn}&fo=json&c=40&at=results,pagination`);
      if (r.status == 200) d = await r.json(); else { L.err = 'search ' + r.status; await sleep(30000); }
    } catch (e) { L.err = String(e); await sleep(30000); }
  }
  if (!d) { L.done = true; return; }
  L.total = d.results.length;
  for (const x of d.results.slice(0, max)) {
    await sleep(2500);
    let p;
    try { p = await tiletext(x); } catch (e) { p = { err: 'net' }; }
    if (p.err) { L.errs++; if (p.err == 'net' || p.err == 503 || p.err == 429) await sleep(30000); continue; }
    L.read++;
    const re = new RegExp(nameRe, 'gi');
    let m, n = 0;
    while ((m = re.exec(p.text)) && n++ < 2) {
      const w = p.text.slice(Math.max(0, m.index - 250), m.index + 350).replace(/\s+/g, ' ');
      L.hits.push([x.date, (/colou?red|negro|\bblack\b/i.test(w) ? '**LABEL** ' : '') + w.slice(100, 420)]);
    }
  }
  L.done = true;
};

// A page's scan, saved to ~/Downloads. tile.loc.gov answers curl with a 403 but
// serves the browser; the file is named by the first argument.
window.savePdf = async (name, date, sp, lccn = 'sn85025007') => {
  const r = await fetch(`https://www.loc.gov/resource/${lccn}/${date}/ed-1/?sp=${sp}&fo=json&at=resource`);
  const pdf = (await r.json()).resource.pdf;
  const b = await (await fetch(pdf)).blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(b); a.download = name + '.pdf';
  document.body.appendChild(a); a.click();
  return b.size;
};
