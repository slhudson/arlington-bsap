# Web access

What each website the sources come from needs from this machine, learned in
September 2026. None of it is in `run.sh`; these are the on-demand routes
behind `data/raw/` and the Drive folder, and they change, so check before
relying on one.

- **Library of Congress, Chronicling America** (the Washington Evening Star
  to 1963, which prints candidates' home streets in the week before an
  election). A JSON API:
  `https://www.loc.gov/collections/chronicling-america/?q=Surname+Arlington&dates=1955-09-01/1955-12-31&fa=partof_title:evening+star+%28washington%2C+d.c.%29+1854-1972&fo=json&c=10&at=results,pagination`;
  each result's resource JSON (`&fo=json&at=resource`) names a
  `fulltext_file` (the OCR text) and a `pdf` (the page). It rate-limits
  after about 55 fetches (a 503, or a Cloudflare page on every route from
  the machine, browsers included); a few minutes clears it, and about 220
  fetches across three pauses is a day's budget. One request every few
  seconds, one worker. A whole-term search on one member costs 20–60
  fetches at 20 results a page, about eight minutes with the pause. The
  Star's story in the week after the 1931 election names each first-Board
  member's section, so for those search "Arlington" and the election week,
  not the name. Two whole-term searches took about 25 minutes with the pause.
- **Virginia Chronicle** (Library of Virginia; the Sun 1935–51, the
  Arlington Daily 1943–48, the Northern Virginia Sun 1957–78). Cloudflare's
  human check blocks curl and the built-in browser; it passes in Sally's own
  Chrome, after which Claude in Chrome can search (`?a=q&txq=Surname&puq=NVS`
  with a date range) and read pages. A page's text needs no login:
  `?a=d&d=<page id>&f=XML`. The page PDF needs the site's free login, which
  Sally has and enters on request; it then opens in Chrome's viewer and the
  download icon saves it as `<page>.pdf`, though Chrome has refused that
  click from a second tab, in which case Sally saves each page herself
  (Cmd+S) at about a page a minute; plan for that. A downloaded PDF's text
  layer differs from the `f=XML` OCR, so identify a page by the id in the
  tab's URL, not by matching text. Title codes for `puq`: TSU the Sun
  (1935–51), TAD the Arlington Daily (1943–48), TDS the Daily Sun
  (1951–56), ALCR the Arlington County Record (1932–33), ANG the
  News-Gazette (1936), NVS the Northern Virginia Sun (1957–78). Addresses sit on the election-week
  jump page, not where the surname is densest: search the surname, then scan
  every hit page's full text for "lives at", "home is at", "resides at" or
  "of <number> North/South"; the Sun's 1947 candidate series and the Daily's
  appointment stories put the street in the first sentence. The OCR
  misreads house numbers (3111 for 3411); read each number off the page
  image before writing a row.
- **Ancestry** (the 1880–1950 censuses with street and house number, race,
  gender, age, occupation). Needs Sally signed in in Chrome. Search by URL:
  `https://www.ancestry.com/search/collections/62308/?name=First_Last&residence=_arlington-arlington-virginia-usa_22922`
  (62308 is 1950, 2442 is 1940, 2441 is 1930). Before 1920 the Arlington
  residence filter finds nothing: use `residence=_virginia-usa_49` and
  filter the results table on "Alexandria". On a record page the
  record's own sheet is the imageviewer link whose `pid` is the record id;
  the first imageviewer link can still be the previously viewed sheet for a
  few seconds. The sheet downloads from the viewer's Save button, "Save to
  your computer", into `~/Downloads` as `<image id>.jpg`, sometimes with
  no extension for 1880 sheets, so add it. A click that lands off the Save
  button fails silently: take the button's ref from `find("Save button")`
  and check `~/Downloads` before moving on. After the first sheet Chrome
  silently blocks every later download from ancestry.com until Sally allows
  the site under `chrome://settings/content/automaticDownloads`; a Save
  click that lands nothing is that, not a missed button. The viewer's Save
  menu only opens in the front tab. A record page's fields read cleanly
  from the tab with JavaScript: the `dt`/`dd` pairs under
  `#recordFieldsContainer`, the household table under the "Household
  Members" heading, and the sheet's viewer link is the first `imageviewer`
  href; the search results table's record links carry the record ids, so a
  surname search filtered to "Alexandria" lists candidates without a click.
  Read a sheet's street labels by cropping at full resolution and rotating 270: they print sideways, and the index misreads both street and house number. Two tabs in one tab group can
  run batches at once. Hill's Arlington
  County directories are not in Ancestry's city-directory collection; its
  Alexandria volumes cover the 1930s and 1940s only.
- **HathiTrust** (Virginia's printed session acts). Cloudflare blocks curl
  but passes in Sally's Chrome. Two catalog records hold them:
  009788135 to about 1904 (1893–94 is `uva.x004737232`) and 009788134
  from 1912, in full view through 1977 and search-only from 1978
  (the 1952 session is `umn.31951d02280223t`). A record's volumes and
  rights list from `catalog.hathitrust.org/api/volumes/brief/recordnumber/<record>.json`,
  fetched in the tab. Inside a volume, `babel.hathitrust.org/cgi/pt/search?q1=<terms>&id=<htid>`
  returns hits with page numbers and context, and `&format=plaintext` on
  a page URL shows that page's OCR and the next few as text. A burst of a dozen page
  fetches draws a 429 for a few minutes: one request at a time.
- **ProQuest** (the Post 1877–2001, including the 11 November 1973
  residence map): a UVA or public-library login; neither was available.
- **washingtonpost.com**: refuses curl and the built-in browser; in Chrome
  the archive pages show two paragraphs once a few have been read, and
  now and then a whole article. The older `wp-dyn` and `wp-srv` pages
  (about 1998–2010) read in full. The Post's own search,
  `washingtonpost.com/search/?query=%22Full+Name%22+Arlington`, works in
  Chrome and lists archive articles back to 1977 with their dates; the
  result links' addresses come from `read_page`, not from clicking, which
  opens nothing. An obituary's or a profile's age is usually in the first
  two paragraphs, so a paywalled page can still give it. Nothing before
  1977 is there: the Northern Virginia Sun on Virginia Chronicle is the
  route for the 1960s.
- **arlingtonva.us and dignitymemorial.com** refuse curl and, mostly,
  automated fetchers, but render in the built-in browser; a page held that
  way is copied into a plain page as text and printed, and the annotation
  says so.
- **Claude in Chrome's JavaScript tool** refuses to return any output that
  contains `?`, `&` or `=`; strip them before returning.
- ARLnow, InsideNoVa, Connection Newspapers, Arlington Magazine, the county
  site and legacy.com fetch with curl and a browser user agent, and print to
  PDF with headless Chrome from the saved HTML with its scripts removed.
  Dignity Memorial and some funeral homes sit behind Cloudflare.
