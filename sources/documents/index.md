# Arlington BSaP: sources archive

Written by `code/archive.py` on 2026-09-25 from commit d423332 of the `slhudson/arlington-bsap` repository. Generated: rerun the script rather than edit it.

- `repository/` is the repository at that commit. `bash run.sh` rebuilds every figure from it; its `README.md` says how. The scans it fetches on demand rather than commits (6 files under `data/raw/us_census_bureau/`) are included at their paths.
- `documents/` holds a copy of every source the report cites that no number is taken from, filed by kind. The first column of each table is the entry's key in `repository/paper/sources.bib`; the entry's `annotation` says what the copy is and when it was taken.

## Documents

One folder per kind. Which folder a copy belongs in is a rule on its bib entry, `kind()` in `code/archive.py`: census: an Ancestry index record and the Census sheet image, in one folder each and then one per census year; press: a newspaper's or magazine's page or article, printed or read online; obituaries; bios: biography pages; campaign websites: candidate sites, questionnaires and campaign material; legal: constitutions, statutes and the like; books: scholarship, including a historical society's magazine; reports: everything else.

### legal (1 entry)

| key | author | date | title | file |
|---|---|---|---|---|
| vaconstitution1902 | Commonwealth of Virginia | 1902 | Constitution of Virginia | `Commonwealth of Virginia 1902 - Constitution of Virginia.pdf` |

### reports (4 entries)

| key | author | date | title | file |
|---|---|---|---|---|
| arlingtonva2016richards | Arlington County | 2016-05-31 | Remembering Tom Richards: A Theodore Roosevelt for Arlington Parks an | `Arlington County 2016 - Remembering Tom Richards.pdf` |
| accf2022 | Arlington County Civic Federation, Task Force in Governance and Election Reform | 2022-06-08 | Resolution on Recommendations | `Arlington County Civic Federation 2022 - TiGER Resolution on Recommendations.pdf` |
| alexandria2024 | City of Alexandria | 2024 | A History of the Boundaries of the City of Alexandria, Virginia: 1749–2024 | `City of Alexandria 2024 - A History of the Boundaries of the City of Alexandria.pdf` |
| hjerpe2021 | Hjerpe, Grace | 2021-07-15 | A History of Representation on the Arlington County Board, 1870–Present | `Hjerpe 2021 - A History of Representation on the Arlington County Board.pdf` |

### books (3 entries)

| key | author | date | title | file |
|---|---|---|---|---|
| anderson1958 | Anderson, Robert Nelson | 1958 | Arlington Adopts the County Manager Form of Government | `Anderson 1958 - Arlington Adopts the County Manager Form of Government.pdf` |
| pratt1995 | Pratt, Sherman W. | 1995-10 | Arlington's At-Large Electoral System: A Study of Its History, Strengths, and Weaknesses | `Pratt 1995 - Arlington's At-Large Electoral System.pdf` |
| rose1964 | Rose, Jr., C. B. | 1964 | Annexation of a Portion of Arlington County by the City of Alexandria in 1915 | `Rose 1964 - Annexation of a Portion of Arlington County by the City of Alexandria.pdf` |

### bios (12 entries)

| key | author | date | title | file |
|---|---|---|---|---|
| arlingtonva2014fisette | Arlington County | 2014 | Jay Fisette - Chair, Arlington County Board | `Arlington County 2014 - Jay Fisette (Wayback Machine capture of 31 March 2014).pdf` |
| arlingtonva2020gutshall | Arlington County | 2020 | Erik Gutshall | `Arlington County 2020 - Erik Gutshall.pdf` |
| arlingtonva2023dorsey | Arlington County | 2023 | Christian Dorsey | `Arlington County 2023 - Christian Dorsey.pdf` |
| arlingtonva2023cristol | Arlington County | 2023 | Katie Cristol | `Arlington County 2023 - Katie Cristol.pdf` |
| arlingtonva2026spain | Arlington County | 2026 | Julius D. "JD" Spain, Sr. | `Arlington County 2026 - Julius D. JD Spain, Sr.pdf` |
| arlingtonva2026deferranti | Arlington County | 2026 | Matt de Ferranti | `Arlington County 2026 - Matt de Ferranti.pdf` |
| arlingtonva2026coffey | Arlington County | 2026 | Maureen Coffey | `Arlington County 2026 - Maureen Coffey.pdf` |
| arlingtonva2026cunningham | Arlington County | 2026 | Susan Cunningham | `Arlington County 2026 - Susan Cunningham.pdf` |
| arlingtonva2026karantonis | Arlington County | 2026 | Takis P. Karantonis | `Arlington County 2026 - Takis P. Karantonis.pdf` |
| lvafisher | Library of Virginia | n.d. | Fisher, Joseph Lyman | `Library of Virginia n.d. - Fisher, Joseph Lyman.pdf` |
| outhistoryfisette | Schlittler, Ron | n.d. | Jay Fisette, Virginia, 1997 | `OutHistory n.d. - Jay Fisette, Virginia, 1997.pdf` |
| vasenatefavola | Senate of Virginia | n.d. | Barbara A. Favola | `Senate of Virginia n.d. - Barbara A. Favola.pdf` |

### campaign websites (3 entries)

| key | author | date | title | file |
|---|---|---|---|---|
| branch2023ferguson | Branch | 2023-08-08 | Paul F. Ferguson platform & website | `Branch 2023 - Paul F. Ferguson platform and website.pdf` |
| cunningham2024 | Susan for Arlington | 2024 | Meet Susan 2024 | `Cunningham 2024 - Meet Susan.pdf` |
| votesmart2021eisenberg | Vote Smart | 2021 | Albert Eisenberg's Biography | `Vote Smart 2021 - Albert Eisenberg's Biography.pdf` |

### press (53 entries)

| key | author | date | title | file |
|---|---|---|---|---|
| arlnow2013zimmerman | ARLnow | 2013-11-06 | UPDATED: Zimmerman Retiring From County Board | `ARLnow 2013 - Zimmerman Retiring From County Board.pdf` |
| arlnow2015 | ARLnow | 2015-06-09 | Cristol, Dorsey Capture County Board Primary | `ARLnow 2015 - Cristol, Dorsey Capture County Board Primary.pdf` |
| arlnow2020 | ARLnow | 2020-05-07 | Takis Karantonis Selected as Democratic Nominee for County Board Special Election | `ARLnow 2020 - Takis Karantonis Selected as Democratic Nominee for County Board Special Election.pdf` |
| arlnow2020b | ARLnow | 2020-04-16 | BREAKING: Former County Board Member Erik Gutshall Has Died | `ARLnow 2020b - Former County Board Member Erik Gutshall Has Died.pdf` |
| arlnow2025 | ARLnow | 2025-12-10 | Local ‘Geezers’ use lunch gatherings to keep tabs on Arlington politics | `ARLnow 2025 - Local Geezers Use Lunch Gatherings to Keep Tabs on Arlington Politics.pdf` |
| connection2002 | Arlington Connection | 2002-05-14 | Zimmerman Wins Democratic Primary | `Arlington Connection 2002 - Zimmerman Wins Democratic Primary.pdf` |
| connection2003 | Arlington Connection | 2003-01-15 | Monroe Dead at 46 | `Arlington Connection 2003 - Monroe Dead at 46.pdf` |
| connection2012 | Arlington Connection | 2012-08-23 | Meet the Arlington County Board | `Arlington Connection 2012 - Meet the Arlington County Board.pdf` |
| field1947 | Field, Dorothy T. | 1947-11-18 | Ashton Heights | `Arlington Daily 1947 - Ashton Heights column by Dorothy T. Field (18 November 1947, p. 2).pdf` |
| tad1947cannon | The Arlington Daily | 1947-11-06 | Chew, Cannon Are Victors In Close Race For County Board: Count Is Complete; Earlier Results Not Changed By Tabulation In Last 2 Precincts | `Arlington Daily 1947 - Chew, Cannon Are Victors In Close Race For County Board (6 November 1947, p. 1).pdf` |
| tad1947cuppett | The Arlington Daily | 1947-05-17 | Cuppett Named To County Board | `Arlington Daily 1947 - Cuppett Named To County Board (17 May 1947, p. 1).pdf` |
| tad1947oath | The Arlington Daily | 1947-05-20 | Cuppett Takes Oath Of Office To Board Post | `Arlington Daily 1947 - Cuppett Takes Oath Of Office To Board Post (20 May 1947, p. 1).pdf` |
| tad1947frisbie | The Arlington Daily | 1947-11-26 | Judge McCarthy Appoints Alfred Frisbie To Fill Vacancy On County Board: Serves Unexpired Term Of The Late Mr. Leo Lloyd | `Arlington Daily 1947 - Judge McCarthy Appoints Alfred Frisbie To Fill Vacancy On County Board (26 November 1947, p. 1).pdf` |
| arlingtonmagazine2018 | Arlington Magazine | 2018-10-30 | 7 Questions with John Vihstadt and Matt de Ferranti | `Arlington Magazine 2018 - 7 Questions with John Vihstadt and Matt de Ferranti.pdf` |
| arlingtonmagazine2020 | Arlington Magazine | 2020-01-31 | 11 Questions with Libby Garvey | `Arlington Magazine 2020 - 11 Questions with Libby Garvey.pdf` |
| barron1960 | Barron, John | 1960-11-09 | Richards Wins in Last Precinct After Grave Fears of Defeat | `Barron 1960 - Richards Wins in Last Precinct After Grave Fears of Defeat (Evening Star, 9 November 1960, p. B-4).pdf` |
| dailysun1952appointees | The Daily Sun | 1952-09-11 | Judge Names 3 County Board Appointees: Picks Byrne, Tillema, Massey; Replaces Dugan, Dean And Cox 'Til After Nov. 4 Vote | `Daily Sun 1952 - Judge Names 3 County Board Appointees (11 September 1952, p. 1).pdf` |
| evans1987 | Evans, Sandra | 1987-03-03 | Brunner to Quit in Arlington | `Evans 1987 - Brunner to Quit in Arlington.pdf` |
| star1934fellows | The Evening Star | 1934-01-23 | Society: Mrs. Harry A. Fellows entertains at a family luncheon | `Evening Star 1934 - Society, Mrs. Harry A. Fellows luncheon (23 January 1934, p. B-3).pdf` |
| star1952detwiler | The Evening Star | 1952-11-05 | Arlington Votes 3 Independents On County Board: George Rowzee, Republican, Takes Full-Term Contest | `Evening Star 1952 - Arlington Votes 3 Independents On County Board (5 November 1952, p. 1, State Edition).pdf` |
| star1957brown | The Evening Star | 1957-09-10 | Arlington Foes: Candidates of Arlington's two major Democratic factions in the county board race | `Evening Star 1957 - Arlington Foes, Magruder and Brown (10 September 1957, p. A-27).pdf` |
| girard1975 | Girard, Keith | 1975-10-16 | GOP Hopefuls Warn Of Bonds | `Girard 1975 - GOP Hopefuls Warn Of Bonds (Northern Virginia Sun, 16 October 1975, p. 2).pdf` |
| hall1993 | Hall, Charles W. | 1993-04-29 | Q. A. with Winslow | `Hall 1993 - Q. A. with Winslow.pdf` |
| helderman2011 | Helderman, Rosalind S. | 2011-02-25 | Sen. Mary Margaret Whipple retiring from Virginia Senate | `Helderman 2011 - Sen. Mary Margaret Whipple Retiring from Virginia Senate.pdf` |
| hsu1987 | Hsu, Evelyn | 1987-12-31 | Arlington Board Is All-Democratic | `Hsu 1987 - Arlington Board Is All-Democratic.pdf` |
| inskeep1931 | Inskeep, Lester N. | 1931-11-05 | District Abolition Fears Are Quieted: Arlington Election Results Show Even Representation on New Board | `Inskeep 1931 - District Abolition Fears Are Quieted (Evening Star, 5 November 1931, p. A-5).pdf` |
| markon2008 | Markon, Jerry | 2008-01-10 | Tejada, Arlington Kick Off Historic Year | `Markon 2008 - Tejada, Arlington Kick Off Historic Year.pdf` |
| mccaffrey2015 | McCaffrey, Scott | 2015-01-29 | Tejada out, Hynes iffy, others circling in Arlington County Board race | `McCaffrey 2015 - Tejada Out, Hynes Iffy, Others Circling in Arlington County Board Race.pdf` |
| mccaffrey2015b | McCaffrey, Scott | 2015-03-06 | Ferguson launches bid for re-election as Arlington clerk of court | `McCaffrey 2015b - Ferguson Launches Bid for Re-election as Arlington Clerk of Court.pdf` |
| mccaffrey2017 | McCaffrey, Scott | 2017-11-15 | Milliken lauded as a beacon of Arlington civic life | `McCaffrey 2017 - Milliken Lauded as a Beacon of Arlington Civic Life.pdf` |
| mccaffrey2018 | McCaffrey, Scott | 2018-11-07 | In final analysis, Vihstadt could not overcome Arlington blue wave | `McCaffrey 2018 - In Final Analysis, Vihstadt Could Not Overcome Arlington Blue Wave.pdf` |
| mccaffrey2022 | McCaffrey, Scott | 2022-07-22 | Death of Dewberry brings back recollections of 1971 campaign | `McCaffrey 2022 - Death of Dewberry Brings Back Recollections of 1971 Campaign.pdf` |
| mccaffrey2024 | McCaffrey, Scott | 2024-11-01 | Four contenders promising to bring winds of change to County Board | `McCaffrey 2024 - Four Contenders Promising to Bring Winds of Change to County Board.pdf` |
| mccaffrey2024b | McCaffrey, Scott | 2024-10-05 | A late bloomer on transportation saluted for exceptional service | `McCaffrey 2024b - A Late Bloomer on Transportation Saluted for Exceptional Service.pdf` |
| mccaffrey2026a | McCaffrey, Scott | 2026-04-03 | Arlington leader took on Virginia's mid-century political machine and paid the price | `McCaffrey 2026a - Arlington Leader Took On Virginia's Mid-Century Political Machine and Paid the Price.pdf` |
| mccaffrey2026b | McCaffrey, Scott | 2026-08-11 | In 1969, the 'silent majority' propelled Arlington GOP to rare political landslide | `McCaffrey 2026b - In 1969, the Silent Majority Propelled Arlington GOP to Rare Political Landslide.pdf` |
| sun1966thomas | Northern Virginia Sun | 1966-11-15 | CCSI Requests Full Support | `Northern Virginia Sun 1966 - CCSI Requests Full Support (15 November 1966, p. 4).pdf` |
| sun1967gop | Northern Virginia Sun | 1967-11-03 | Arlington GOP Seeks to Maintain Board Control | `Northern Virginia Sun 1967 - Arlington GOP Seeks to Maintain Board Control (3 November 1967, p. 20).pdf` |
| cadman1973 | Cadman, Anne | 1973-10-23 | Three Vie For Board Seat | `Northern Virginia Sun 1973 - Pratt, Lampe, Bozman Vie For Board Seat (23 October 1973, p. 2).pdf` |
| sun1975grotos | Northern Virginia Sun | 1975-10-22 | Grotos 'Friends' Operate Office | `Northern Virginia Sun 1975 - Grotos 'Friends' Operate Office (22 October 1975, p. 3).pdf` |
| patch2021 | Patch | 2021-05-20 | Candidate Profile: Takis Karantonis For Arlington County Board | `Patch 2021 - Candidate Profile, Takis Karantonis for Arlington County Board.pdf` |
| patch2024 | Patch | 2024-09-03 | Julius D. 'JD' Spain Sr. Runs For Arlington County Board: 2024 Profile | `Patch 2024 - Julius D. JD Spain Sr. Runs for Arlington County Board, 2024 Profile.pdf` |
| patch2026 | Patch | 2026-06-12 | Matt de Ferranti Running For Reelection In Democratic Primary: Candidate Questionnaire | `Patch 2026 - Matt de Ferranti Running for Reelection in Democratic Primary, Candidate Questionnaire.pdf` |
| pope2012 | Pope, Michael Lee | 2012-10-10 | Freshman Arlington County Board Member Faces Two Opponents in November | `Pope 2012 - Freshman Arlington County Board Member Faces Two Opponents in November.pdf` |
| pope2014 | Pope, Michael Lee | 2014-02-05 | Special Election Down the Pike for Arlington County Board | `Pope 2014 - Special Election Down the Pike for Arlington County Board.pdf` |
| preston1955 | Preston, Alex R. | 1955-11-02 | AIM to Control Board Regardless of Election | `Preston 1955 - AIM to Control Board Regardless of Election (Evening Star, 2 November 1955, p. B-2).pdf` |
| rothstein2015 | Rothstein, Ethan | 2015-02-04 | County Board Chair Hynes Announces Retirement | `Rothstein 2015 - County Board Chair Hynes Announces Retirement.pdf` |
| sullivan2013 | Sullivan, Patricia | 2013-12-23 | Arlington's Chris Zimmerman, advocate for smart growth, is leaving public office | `Sullivan 2013 - Arlington's Chris Zimmerman, Advocate for Smart Growth, Is Leaving Public Office.pdf` |
| sun1947candidates | The Sun | 1947-10-24 | Fourth of a Series: Candidates for the County Board | `Sun 1947 - Fourth of a Series, Candidates for the County Board (24 October 1947, p. 3).pdf` |
| sun1938womenvoters | The Sun | 1938-11-18 | Women Voters Again Elect Mrs. Simpson | `The Sun 1938 - Women Voters Again Elect Mrs. Simpson (18 November 1938, p. 4).pdf` |
| post1980 | The Washington Post | 1980-01-25 | John Purdy to Leave Arlington Board | `Washington Post 1980 - John Purdy to Leave Arlington Board.pdf` |
| post1991 | The Washington Post | 1991-08-28 | Ned Randolph Thomas Sr. | `Washington Post 1991 - Ned Randolph Thomas Sr.pdf` |
| post1998 | The Washington Post | 1998 | Va. Voters' Guide '98: County Board | `Washington Post 1998 - Va. Voters' Guide '98, Arlington County Board.pdf` |

### obituaries (10 entries)

| key | author | date | title | file |
|---|---|---|---|---|
| tad1947lloyd | The Arlington Daily | 1947-11-03 | Leo C. Lloyd, County Board Member, Dies Suddenly Today: Stomach Ailment Is Fatal To Former Chairman Of Board, Resident Of County For 30 Years | `Arlington Daily 1947 - Leo C. Lloyd, County Board Member, Dies Suddenly Today (3 November 1947, p. 1).pdf` |
| lowry2021 | Dignity Memorial | 2021 | Roye Lowry Obituary | `Dignity Memorial 2021 - Roye Lowry Obituary.pdf` |
| wholey2023 | Dignity Memorial | 2023 | Joseph Wholey Obituary | `Dignity Memorial 2023 - Joseph Wholey Obituary.pdf` |
| detwiler2017 | The Washington Post, via Legacy.com | 2017-10-08 | Stephen Detwiler Obituary | `Legacy.com 2017 - Stephen Detwiler Obituary.pdf` |
| ricks2021 | The Washington Post, via Legacy.com | 2021 | Jay Ricks Obituary (1932-2021) | `Legacy.com 2021 - Jay Ricks Obituary.pdf` |
| munsey2025 | The Washington Post, via Legacy.com | 2025 | Virdell Munsey Obituary (1933-2025) | `Legacy.com 2025 - Virdell Munsey Obituary.pdf` |
| mccaffrey2009 | McCaffrey, Scott | 2009-01-09 | Ellen Bozman Dies at 83; Spent Record Tenure on County Board | `McCaffrey 2009 - Ellen Bozman Dies at 83; Spent Record Tenure on County Board.pdf` |
| mccaffrey2019 | McCaffrey, Scott | 2019-04-30 | Two-term Arlington board member Dorothy Grotos dies at 88 | `McCaffrey 2019 - Two-Term Arlington Board Member Dorothy Grotos Dies at 88.pdf` |
| mccaffrey2022b | McCaffrey, Scott | 2022-11-22 | Obituary: Eisenberg seen as conduit to modern, progressive Arlington | `McCaffrey 2022b - Obituary, Eisenberg Seen as Conduit to Modern, Progressive Arlington.pdf` |
| pearson1998 | Pearson, Richard | 1998-01-06 | James B. Hunter Dies at 58 | `Pearson 1998 - James B. Hunter Dies at 58.pdf` |

### census (53 entries)

| key | author | date | title | file |
|---|---|---|---|---|
| census1880grunwell | U.S. Bureau of the Census | 1880-06-01 | A. B. Grunwell in the 1880 United States Federal Census, Alexandria County, Virginia | `Ancestry 1880 - A. B. Grunwell in the 1880 United States Federal Census (record 11856251).pdf`<br>`US Census 1880 - Alexandria County VA, ED 8, page 451D (Samuel Titus, A B Grunwell).jpg` |
| census1880costello | U.S. Bureau of the Census | 1880-06-01 | Christopher Costello in the 1880 United States Federal Census, Alexandria County, Virginia | `Ancestry 1880 - Christopher Costello in the 1880 United States Federal Census (record 42596550).pdf`<br>`US Census 1880 - Alexandria County VA, ED 8, page 454A (Christopher Costello).jpg` |
| census1880hume | U.S. Bureau of the Census | 1880-06-01 | Frank Hume in the 1880 United States Federal Census, Alexandria County, Virginia | `Ancestry 1880 - Frank Hume in the 1880 United States Federal Census (record 13142083).pdf`<br>`US Census 1880 - Alexandria County VA, ED 7, page 438C (Frank Hume).jpg` |
| census1880corbett | U.S. Bureau of the Census | 1880-06-01 | Frederick S. Corbett in the 1880 United States Federal Census, Alexandria County, Virginia | `Ancestry 1880 - Frederick S. Corbett in the 1880 United States Federal Census (record 42596119).pdf`<br>`US Census 1880 - Alexandria County VA, ED 6, page 422B (William A Rowe, Frederick S Corbett).jpg` |
| census1880veitch | U.S. Bureau of the Census | 1880-06-01 | George W. Veitch in the 1880 United States Federal Census, Alexandria County, Virginia | `Ancestry 1880 - George W. Veitch in the 1880 United States Federal Census (record 11855321).pdf`<br>`US Census 1880 - Alexandria County VA, ED 6, page 422A (George Veitch).jpg` |
| census1880febrey | U.S. Bureau of the Census | 1880-06-01 | Henry W. Febrey in the 1880 United States Federal Census, Alexandria County, Virginia | `Ancestry 1880 - Henry W. Febrey in the 1880 United States Federal Census (record 42596547).pdf`<br>`US Census 1880 - Alexandria County VA, ED 8, page 451C (Henry Febrey).jpg` |
| census1880ball | U.S. Bureau of the Census | 1880-06-01 | Horatio Ball in the 1880 United States Federal Census, Alexandria County, Virginia | `Ancestry 1880 - Horatio Ball in the 1880 United States Federal Census (record 42596079).pdf`<br>`US Census 1880 - Alexandria County VA, ED 6, page 425C (Horatio Ball).jpg` |
| census1880syphax | U.S. Bureau of the Census | 1880-06-01 | John B. Syphax in the 1880 United States Federal Census, Alexandria County, Virginia | `Ancestry 1880 - John B. Syphax in the 1880 United States Federal Census (record 11855248).pdf`<br>`US Census 1880 - Alexandria County VA, ED 6, page 417D (John Syphax).jpg` |
| census1880squier | U.S. Bureau of the Census | 1880-06-01 | Perkins W. Squier in the 1880 United States Federal Census, Alexandria County, Virginia | `Ancestry 1880 - Perkins W. Squier in the 1880 United States Federal Census (record 13141145).pdf`<br>`US Census 1880 - Alexandria County VA, ED 6, page 430B (Perkins Squier).jpg` |
| census1880titus | U.S. Bureau of the Census | 1880-06-01 | Samuel Titus in the 1880 United States Federal Census, Alexandria County, Virginia | `Ancestry 1880 - Samuel Titus in the 1880 United States Federal Census (record 18551753).pdf` |
| census1880allen | U.S. Bureau of the Census | 1880-06-01 | Tibbett Allen in the 1880 United States Federal Census, Alexandria County, Virginia | `Ancestry 1880 - Tibbett Allen in the 1880 United States Federal Census (record 42596239).pdf`<br>`US Census 1880 - Alexandria County VA, ED 7, page 440C (Tibbett Allen).jpg` |
| census1880pinn | U.S. Bureau of the Census | 1880-06-01 | Travis B. Pinn in the 1880 United States Federal Census, Alexandria County, Virginia | `Ancestry 1880 - Travis B. Pinn in the 1880 United States Federal Census (record 11855799).pdf`<br>`US Census 1880 - Alexandria County VA, ED 7, page 434D (Travis B Pinn).jpg` |
| census1880rowe | U.S. Bureau of the Census | 1880-06-01 | William A. Rowe in the 1880 United States Federal Census, Alexandria County, Virginia | `Ancestry 1880 - William A. Rowe in the 1880 United States Federal Census (record 18550599).pdf` |
| census1900costello | U.S. Bureau of the Census | 1900-06-01 | Christopher J. Costello in the 1900 United States Federal Census, Alexandria County, Virginia | `Ancestry 1900 - Christopher J. Costello in the 1900 United States Federal Census (record 71172445).pdf`<br>`US Census 1900 - Alexandria County VA, ED 3, sheet 9 (Christopher J Costello).jpg` |
| census1900darbey | U.S. Bureau of the Census | 1900-06-01 | Rezin W. Darbey in the 1900 United States Federal Census, Alexandria County, Virginia | `Ancestry 1900 - Rezin W. Darbey in the 1900 United States Federal Census (record 71168793).pdf`<br>`US Census 1900 - Alexandria County VA, ED 1, sheet 22 (Rezin W Darby).jpg` |
| census1910febrey | U.S. Bureau of the Census | 1910-06-01 | W. N. Febrey County in the 1910 United States Federal Census, Alexandria County, Virginia | `Ancestry 1910 - W. N. Febrey County in the 1910 United States Federal Census (record 29043354).pdf`<br>`US Census 1910 - Alexandria County VA, ED 14, sheet 15A (William N Febrey).jpg` |
| census1930delashmutt | U.S. Bureau of the Census | 1930-04-01 | Basil M. DeLashmutt in the 1930 United States Federal Census, Arlington County, Virginia | `Ancestry 1930 - Basil M. DeLashmutt in the 1930 United States Federal Census (record 97289483).pdf`<br>`US Census 1930 - Arlington VA, ED 19, sheet 9A (Basil M Delashmutt).jpg` |
| census1930fellows | U.S. Bureau of the Census | 1930-04-01 | Harry A. Fellows in the 1930 United States Federal Census, Arlington County, Virginia | `Ancestry 1930 - Harry A. Fellows in the 1930 United States Federal Census (record 97282655).pdf`<br>`US Census 1930 - Arlington VA, ED 17, sheet 3A (Harry A Fellows).jpg` |
| census1930mcshea | U.S. Bureau of the Census | 1930-04-01 | W. A. E. McShea in the 1930 United States Federal Census, Arlington County, Virginia | `Ancestry 1930 - W. A. E. McShea in the 1930 United States Federal Census (record 97276453).pdf`<br>`US Census 1930 - Arlington VA, ED 6, sheet 14B (William McShea).jpg` |
| census1940garnett | U.S. Bureau of the Census | 1940-04-01 | Christopher B. Garnett in the 1940 United States Federal Census, Arlington County, Virginia | `Ancestry 1940 - Christopher B. Garnett in the 1940 United States Federal Census (record 16648555).pdf`<br>`US Census 1940 - Arlington VA, sheet 8B (Christopher B Garnett).jpg` |
| census1940dugan | U.S. Bureau of the Census | 1940-04-01 | Daniel A. Dugan in the 1940 United States Federal Census, Arlington County, Virginia | `Ancestry 1940 - Daniel A. Dugan in the 1940 United States Federal Census (record 16694523).pdf`<br>`US Census 1940 - Arlington VA, sheet 10B (Dan A Dugan).jpg` |
| census1940campbell | U.S. Bureau of the Census | 1940-04-01 | Edmund D. Campbell in the 1940 United States Federal Census, Arlington County, Virginia | `Ancestry 1940 - Edmund D. Campbell in the 1940 United States Federal Census (record 16651594).pdf`<br>`US Census 1940 - Arlington VA, sheet 1A (Edmund D Campbell).jpg` |
| census1940magruder | U.S. Bureau of the Census | 1940-04-01 | Elizabeth B. Magruder in the 1940 United States Federal Census, Arlington County, Virginia | `Ancestry 1940 - Elizabeth B. Magruder in the 1940 United States Federal Census (record 16677660).pdf`<br>`US Census 1940 - Arlington VA, sheet 2B (Elizabeth B Magruder).jpg` |
| census1940chew | U.S. Bureau of the Census | 1940-04-01 | F. Freeland Chew in the 1940 United States Federal Census, Arlington County, Virginia | `Ancestry 1940 - F. Freeland Chew in the 1940 United States Federal Census (record 16670151).pdf`<br>`US Census 1940 - Arlington VA, sheet 21B (F Freeland Chew).jpg` |
| census1940gosnell | U.S. Bureau of the Census | 1940-04-01 | Fred A. Gosnell, Sr in the 1940 United States Federal Census, Arlington County, Virginia | `Ancestry 1940 - Fred A. Gosnell, Sr in the 1940 United States Federal Census (record 16686371).pdf`<br>`US Census 1940 - Arlington VA, sheet 28B (Fred A Gosnell).jpg` |
| census1940yeatman | U.S. Bureau of the Census | 1940-04-01 | George M. Yeatman in the 1940 United States Federal Census, Arlington County, Virginia | `Ancestry 1940 - George M. Yeatman in the 1940 United States Federal Census (record 16893386).pdf`<br>`US Census 1940 - Arlington VA, sheet 12A (George M Yeatman).jpg` |
| census1940gall | U.S. Bureau of the Census | 1940-04-01 | John C. Gall in the 1940 United States Federal Census, Arlington County, Virginia | `Ancestry 1940 - John C. Gall in the 1940 United States Federal Census (record 16648495).pdf`<br>`US Census 1940 - Arlington VA, sheet 8A (John C Gall).jpg` |
| census1940lloyd | U.S. Bureau of the Census | 1940-04-01 | Leo C. Lloyd in the 1940 United States Federal Census, Arlington County, Virginia | `Ancestry 1940 - Leo C. Lloyd in the 1940 United States Federal Census (record 16674130).pdf`<br>`US Census 1940 - Arlington VA, sheet 14A (Leo C Lloyd).jpg` |
| census1940kelley | U.S. Bureau of the Census | 1940-04-01 | Lyman M. Kelley in the 1940 United States Federal Census, Arlington County, Virginia | `Ancestry 1940 - Lyman M. Kelley in the 1940 United States Federal Census (record 16677443).pdf`<br>`US Census 1940 - Arlington VA, sheet 1A (Lyman Kelley).jpg` |
| census1940detwiler | U.S. Bureau of the Census | 1940-04-01 | Robert H. Detwiler in the 1940 United States Federal Census, Arlington County, Virginia | `Ancestry 1940 - Robert H. Detwiler in the 1940 United States Federal Census (record 16671752).pdf`<br>`US Census 1940 - Arlington VA, sheet 62A (Robert H Detweiler).jpg` |
| census1940ames | U.S. Bureau of the Census | 1940-04-01 | W. P. Ames in the 1940 United States Federal Census, Arlington County, Virginia | `Ancestry 1940 - W. P. Ames in the 1940 United States Federal Census (record 16894163).pdf`<br>`US Census 1940 - Arlington VA, sheet 21B (William P Ames).jpg` |
| census1950dean | U.S. Bureau of the Census | 1950-04-01 | Alan L. Dean in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Alan L. Dean in the 1950 United States Federal Census (record 112277777).pdf`<br>`US Census 1950 - Arlington VA, ED 27-694, sheet 8 (Alan L Dean).jpg` |
| census1950frisbie | U.S. Bureau of the Census | 1950-04-01 | Alfred E. Frisbie in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Alfred E. Frisbie in the 1950 United States Federal Census (record 111604905).pdf`<br>`US Census 1950 - Arlington VA, ED 27-713, image 14 (Alfred E Frisbie).jpg` |
| census1950kimel | U.S. Bureau of the Census | 1950-04-01 | Alvin F. Kimel in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Alvin F. Kimel in the 1950 United States Federal Census (record 112018500).pdf`<br>`US Census 1950 - Arlington VA, ED 27-599, image 36 (Alvin F Kimel).jpg` |
| census1950krupsaw | U.S. Bureau of the Census | 1950-04-01 | DavidL. Krupsaw in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - DavidL. Krupsaw in the 1950 United States Federal Census (record 112715962).pdf`<br>`US Census 1950 - Arlington VA, ED 27-715, image 9 (David L Krupsaw).jpg` |
| census1950haggerty | U.S. Bureau of the Census | 1950-04-01 | Dr. Kenneth M. Haggerty in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Dr. Kenneth M. Haggerty in the 1950 United States Federal Census (record 113700637).pdf`<br>`US Census 1950 - Arlington VA, ED 27-613, sheet 36 (Kenneth M Haggerty).jpg` |
| census1950campbell | U.S. Bureau of the Census | 1950-04-01 | Edmund D. Campbell in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Edmund D. Campbell in the 1950 United States Federal Census (record 113809320).pdf`<br>`US Census 1950 - Arlington VA, ED 27-571, sheet 5 (Edmund D Campbell).jpg` |
| census1950magruder | U.S. Bureau of the Census | 1950-04-01 | Elizabeth B. Magruder in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Elizabeth B. Magruder in the 1950 United States Federal Census (record 113984778).pdf`<br>`US Census 1950 - Arlington VA, ED 27-620, image 4 (Elizabeth B Magruder).jpg` |
| census1950wilt | U.S. Bureau of the Census | 1950-04-01 | Ernest D. Wilt in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Ernest D. Wilt in the 1950 United States Federal Census (record 113258354).pdf`<br>`US Census 1950 - Arlington VA, ED 27-577, image 5 (Ernest D Wilt).jpg` |
| census1950chew | U.S. Bureau of the Census | 1950-04-01 | F. Freeland Chew in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - F. Freeland Chew in the 1950 United States Federal Census (record 113552739).pdf`<br>`US Census 1950 - Arlington VA, ED 27-586, image 26 (Freeland Chew).jpg` |
| census1950cannon | U.S. Bureau of the Census | 1950-04-01 | Florence Cannon in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Florence Cannon in the 1950 United States Federal Census (record 111693367).pdf`<br>`US Census 1950 - Arlington VA, ED 27-638, image 33 (Florence Cannon).jpg` |
| census1950rowzee | U.S. Bureau of the Census | 1950-04-01 | George M. Rowzee, Jr in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - George M. Rowzee, Jr in the 1950 United States Federal Census (record 113471251).pdf`<br>`US Census 1950 - Arlington VA, ED 27-690, image 8 (George M Rowzee Jr).jpg` |
| census1950cuppett | U.S. Bureau of the Census | 1950-04-01 | Harry W. Cuppett in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Harry W. Cuppett in the 1950 United States Federal Census (record 111634941).pdf`<br>`US Census 1950 - Arlington VA, ED 27-619, sheet 37 (Harry W Cuppett).jpg` |
| census1950massey | U.S. Bureau of the Census | 1950-04-01 | Howard R. Massey in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Howard R. Massey in the 1950 United States Federal Census (record 112780053).pdf`<br>`US Census 1950 - Arlington VA, ED 27-592, image 24 (Howard R Massey).jpg` |
| census1950tillema | U.S. Bureau of the Census | 1950-04-01 | John A. Tillema in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - John A. Tillema in the 1950 United States Federal Census (record 111340709).pdf`<br>`US Census 1950 - Arlington VA, ED 27-606, image 23 (John A Tillema).jpg` |
| census1950urbanske | U.S. Bureau of the Census | 1950-04-01 | Leo Urbanske, Jr in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Leo Urbanske, Jr in the 1950 United States Federal Census (record 111721290).pdf`<br>`US Census 1950 - Arlington VA, ED 27-707, image 8 (Leo Urbanske Jr).jpg` |
| census1950buchholz | U.S. Bureau of the Census | 1950-04-01 | Leone B. Buchholz in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Leone B. Buchholz in the 1950 United States Federal Census (record 111102514).pdf`<br>`US Census 1950 - Arlington VA, ED 27-714, image 36 (Leona B Buckholz).jpg` |
| census1950blevins | U.S. Bureau of the Census | 1950-04-01 | Lucas H. Blevins in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Lucas H. Blevins in the 1950 United States Federal Census (record 113809451).pdf`<br>`US Census 1950 - Arlington VA, ED 27-571, image 9 (Lucas H Blevins).jpg` |
| census1950byrne | U.S. Bureau of the Census | 1950-04-01 | M. Rex Byrne in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - M. Rex Byrne in the 1950 United States Federal Census (record 110628239).pdf`<br>`US Census 1950 - Arlington VA, ED 27-652, image 24 (M Rector Byrne).jpg` |
| census1950kaul | U.S. Bureau of the Census | 1950-04-01 | Ralph Kaul in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Ralph Kaul in the 1950 United States Federal Census (record 110687602).pdf`<br>`US Census 1950 - Arlington VA, ED 27-664, image 8 (Ralph P Kaul).jpg` |
| census1950peck | U.S. Bureau of the Census | 1950-04-01 | Robert A. Peck in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Robert A. Peck in the 1950 United States Federal Census (record 111900083).pdf`<br>`US Census 1950 - Arlington VA, ED 27-593, image 15 (Robert A Peck).jpg` |
| census1950cox | U.S. Bureau of the Census | 1950-04-01 | RobertW. Cox in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - RobertW. Cox in the 1950 United States Federal Census (record 112424788).pdf`<br>`US Census 1950 - Arlington VA, ED 27-674, image 4 (Robert W Cox).jpg` |
| census1950cooper | U.S. Bureau of the Census | 1950-04-01 | Wesley W. Cooper in the 1950 United States Federal Census, Arlington County, Virginia | `Ancestry 1950 - Wesley W. Cooper in the 1950 United States Federal Census (record 113202944).pdf`<br>`US Census 1950 - Arlington VA, ED 27-629, image 22 (Wesley W Cooper).jpg` |

## Sources held in the repository

Entries whose copy is under `repository/data/raw/`, because a number is taken from it.

| key | author | date | title | in data/raw/ |
|---|---|---|---|---|
| oleary2010 | O'Leary, Frank | 2010-03 | The Electoral History of That Part of Alexandria County Now Known as Arlington County, 1870–1920 | `data/raw/arlington_county/electoral_history_1870-1920.pdf` |
| arlingtonelections2021 | Arlington County Office of Voter Registration and Elections | 2021-11-18 | Arlington County Election Results | `data/raw/arlington_county/candidate_history_1920-present.pdf` |
| novack1994 | Novack, Norman S. | 1994-10 | Six Decades of Arlington Leadership | `data/raw/arlington_historical_magazine/novack_six_decades_of_arlington_leadership_1994.pdf` |
| vaelections | Virginia Department of Elections | n.d. | Historical Elections Database | `data/raw/va_dept_of_elections/county_board_2000-2026.csv`<br>`data/raw/va_dept_of_elections/president_1924-2024.csv` |
| varegistration | Virginia Department of Elections | n.d. | Registration Statistics | `data/raw/va_dept_of_elections/registration_2010-2025.csv` |
| forstall1996 | Forstall, Richard L. | 1996 | Population of States and Counties of the United States: 1790–1990 | `data/raw/us_census_bureau/population_of_states_and_counties_1790-1990_virginia.pdf` |
| walker1872 | Walker, Francis A. | 1872 | The Statistics of the Population of the United States | `data/raw/us_census_bureau/1870/1870a-01.pdf`<br>`data/raw/us_census_bureau/1870/1870a-04.pdf`<br>`data/raw/us_census_bureau/1870/1870a-09.pdf` |
| census1880 | U.S. Department of the Interior, Census Office | 1880 | Statistics of the Population of the United States at the Tenth Census (June 1, 1880) | `data/raw/us_census_bureau/1880/1880_v1-01.pdf`<br>`data/raw/us_census_bureau/1880/1880_v1-12.pdf`<br>`data/raw/us_census_bureau/1880/1880_v1-13.pdf` |
| census1890 | U.S. Department of the Interior, Census Office | 1895 | Report on Population of the United States at the Eleventh Census: 1890 | `data/raw/us_census_bureau/1890/1890a_v1-01.pdf`<br>`data/raw/us_census_bureau/1890/1890a_v1-11.pdf`<br>`data/raw/us_census_bureau/1890/1890a_v1-12.pdf`<br>`data/raw/us_census_bureau/1890/1890a_v1-13.pdf`<br>`data/raw/us_census_bureau/1890/1890a_v1-14.pdf` |
| censusbureau1990twps76 | U.S. Bureau of the Census | 1990 | Race and Hispanic Origin for Selected Large Cities and Other Places: Earliest Census to 1990 | `data/raw/us_census_bureau/1990/pop-twps0076_virginia_1990.pdf` |
| censusapi | U.S. Census Bureau | n.d. | Decennial Census Summary File and Redistricting Data | `data/raw/us_census_bureau/2000/censusapi_dec_sf1_P003_race_virginia_counties.csv`<br>`data/raw/us_census_bureau/2000/censusapi_dec_sf1_P005_race_18_and_over_virginia_counties.csv`<br>`data/raw/us_census_bureau/2000/censusapi_dec_sf1_P008_hispanic_origin_by_race_virginia_counties.csv`<br>`data/raw/us_census_bureau/2000/censusapi_dec_sf1_variables.csv`<br>`data/raw/us_census_bureau/2010/censusapi_dec_sf1_P10_race_18_and_over_virginia_counties.csv`<br>`data/raw/us_census_bureau/2010/censusapi_dec_sf1_P3_race_virginia_counties.csv`<br>`data/raw/us_census_bureau/2010/censusapi_dec_sf1_P5_hispanic_origin_by_race_virginia_counties.csv`<br>`data/raw/us_census_bureau/2010/censusapi_dec_sf1_variables.csv`<br>`data/raw/us_census_bureau/2020/censusapi_dec_pl_P1_race_virginia_counties.csv`<br>`data/raw/us_census_bureau/2020/censusapi_dec_pl_P2_hispanic_origin_by_race_virginia_counties.csv`<br>`data/raw/us_census_bureau/2020/censusapi_dec_pl_P3_race_18_and_over_virginia_counties.csv`<br>`data/raw/us_census_bureau/2020/censusapi_dec_pl_variables.csv` |
| sun1938referendum | The Sun | 1938-11-11 | Referendum Wins By 61 Votes; Board Will Be 'Staggered' | `data/raw/arlington_sun/sun_1938-11-11_p1.pdf` |
| census1980stf1a | U.S. Bureau of the Census | n.d. | Census of Population and Housing, 1980: Summary Tape File 1A, Virginia | `data/raw/us_census_bureau/1980/1980_stf1_datadict.txt`<br>`data/raw/us_census_bureau/1980/stf1a_table10_age_virginia_counties.csv`<br>`data/raw/us_census_bureau/1980/stf1a_table10_female_by_age_virginia_counties.csv`<br>`data/raw/us_census_bureau/1980/stf1a_table7_race_virginia_counties.csv`<br>`data/raw/us_census_bureau/1980/stf1a_table8_spanish_origin_virginia_counties.csv`<br>`data/raw/us_census_bureau/1980/stf1a_table9_race_of_spanish_origin_virginia_counties.csv` |
| census1990stf1a | U.S. Bureau of the Census | n.d. | Census of Population and Housing, 1990: Summary Tape File 1A, Virginia | `data/raw/us_census_bureau/1990/stf1a_age_virginia_counties.csv`<br>`data/raw/us_census_bureau/1990/stf1a_hispanic_origin_by_race_virginia_counties.csv`<br>`data/raw/us_census_bureau/1990/stf1a_race_virginia_counties.csv` |

Every file under `data/raw/`, from `data/contents.csv`: what it is, who published it, and the first sixteen hex digits of its SHA-256.

| path | source | sha256 | committed |
|---|---|---|---|
| `data/raw/arlington_county/candidate_history_1920-present.pdf` | Arlington County Office of Voter Registration and Elections, Arlington County Election Results (Candidate History, 1920-Present), last updated 18 November 2021 (arlingtonelections2021) | `5fa7deaf1c8f91f9` | yes |
| `data/raw/arlington_county/electoral_history_1870-1920.pdf` | Frank O'Leary, The Electoral History of That Part of Alexandria County Now Known as Arlington County, 1870-1920, version 2, March 2010 (oleary2010) | `a3285a7dce013e4a` | yes |
| `data/raw/arlington_historical_magazine/novack_six_decades_of_arlington_leadership_1994.pdf` | Norman S. Novack, Six Decades of Arlington Leadership, Arlington Historical Magazine, 1994 (novack1994) | `8a9483e226743b35` | yes |
| `data/raw/arlington_sun/sun_1938-11-11_p1.pdf` | The Sun (Arlington), 11 November 1938, p.1, via the Library of Virginia's Virginia Chronicle (sun1938referendum) | `1e955e238e45baac` | yes |
| `data/raw/us_census_bureau/1870/1870a-01.pdf` | U.S. Census Bureau, 1870 census volume I, chunk 1, as chunked on census.gov (walker1872) | `207a404c63c65609` | yes |
| `data/raw/us_census_bureau/1870/1870a-04.pdf` | U.S. Census Bureau, 1870 census volume I, chunk 4, as chunked on census.gov (walker1872) | `0dc7a2a508ffe416` | yes |
| `data/raw/us_census_bureau/1870/1870a-09.pdf` | U.S. Census Bureau, 1870 census volume I, chunk 9, as chunked on census.gov (walker1872) | `63f3d4eaac112736` | yes |
| `data/raw/us_census_bureau/1880/1880_v1-01.pdf` | U.S. Census Bureau, 1880 census volume I, chunk 1, as chunked on census.gov (census1880) | `58f0cadb9d44fff9` | yes |
| `data/raw/us_census_bureau/1880/1880_v1-12.pdf` | U.S. Census Bureau, 1880 census volume I, chunk 12, as chunked on census.gov (census1880) | `acc0b1ab4dd6ee88` | no, fetched on demand; in this archive |
| `data/raw/us_census_bureau/1880/1880_v1-13.pdf` | U.S. Census Bureau, 1880 census volume I, chunk 13, as chunked on census.gov (census1880) | `6e859908a8bd2a5d` | no, fetched on demand; in this archive |
| `data/raw/us_census_bureau/1890/1890a_v1-01.pdf` | U.S. Census Bureau, 1890 census volume I part 1, chunk 1, as chunked on census.gov (census1890) | `0f79bb0363c8e67b` | yes |
| `data/raw/us_census_bureau/1890/1890a_v1-11.pdf` | U.S. Census Bureau, 1890 census volume I part 1, chunk 11, as chunked on census.gov (census1890) | `47903c2e2ec9ed46` | no, fetched on demand; in this archive |
| `data/raw/us_census_bureau/1890/1890a_v1-12.pdf` | U.S. Census Bureau, 1890 census volume I part 1, chunk 12, as chunked on census.gov (census1890) | `782da690cdf3ca40` | no, fetched on demand; in this archive |
| `data/raw/us_census_bureau/1890/1890a_v1-13.pdf` | U.S. Census Bureau, 1890 census volume I part 1, chunk 13, as chunked on census.gov (census1890) | `fb1d9e704366cbf4` | no, fetched on demand; in this archive |
| `data/raw/us_census_bureau/1890/1890a_v1-14.pdf` | U.S. Census Bureau, 1890 census volume I part 1, chunk 14, as chunked on census.gov (census1890) | `42c36586ed15d9f0` | no, fetched on demand; in this archive |
| `data/raw/us_census_bureau/1980/1980_stf1_datadict.txt` | U.S. Census Bureau, 1980 Summary Tape File 1 record layout (census1980stf1a) | `70dfc445c806a869` | yes |
| `data/raw/us_census_bureau/1980/stf1a_table10_age_virginia_counties.csv` | U.S. Census Bureau, 1980 STF1A, Virginia county-level geographies (census1980stf1a) | `2cda4f51703f2e0c` | yes |
| `data/raw/us_census_bureau/1980/stf1a_table10_female_by_age_virginia_counties.csv` | U.S. Census Bureau, 1980 STF1A, Virginia county-level geographies (census1980stf1a) | `c4345b6aee24d6ba` | yes |
| `data/raw/us_census_bureau/1980/stf1a_table7_race_virginia_counties.csv` | U.S. Census Bureau, 1980 STF1A, Virginia county-level geographies (census1980stf1a) | `3c186d6b5a0b1857` | yes |
| `data/raw/us_census_bureau/1980/stf1a_table8_spanish_origin_virginia_counties.csv` | U.S. Census Bureau, 1980 STF1A, Virginia county-level geographies (census1980stf1a) | `a5eb287997ec5b60` | yes |
| `data/raw/us_census_bureau/1980/stf1a_table9_race_of_spanish_origin_virginia_counties.csv` | U.S. Census Bureau, 1980 STF1A, Virginia county-level geographies (census1980stf1a) | `36cd5a39d70acb1c` | yes |
| `data/raw/us_census_bureau/1990/pop-twps0076_virginia_1990.pdf` | U.S. Census Bureau, working paper POP-TWPS0076, Virginia table (censusbureau1990twps76) | `d95ce7a22270b322` | yes |
| `data/raw/us_census_bureau/1990/stf1a_age_virginia_counties.csv` | U.S. Census Bureau, 1990 STF1A, Virginia county-level geographies (census1990stf1a) | `eca29df147336abb` | yes |
| `data/raw/us_census_bureau/1990/stf1a_hispanic_origin_by_race_virginia_counties.csv` | U.S. Census Bureau, 1990 STF1A, Virginia county-level geographies (census1990stf1a) | `40c9d702153025ae` | yes |
| `data/raw/us_census_bureau/1990/stf1a_race_virginia_counties.csv` | U.S. Census Bureau, 1990 STF1A, Virginia county-level geographies (census1990stf1a) | `b03d595b22210921` | yes |
| `data/raw/us_census_bureau/2000/censusapi_dec_sf1_P003_race_virginia_counties.csv` | U.S. Census Bureau, 2000 census via the Census API (censusapi), every Virginia county | `9dbaa46934f376af` | yes |
| `data/raw/us_census_bureau/2000/censusapi_dec_sf1_P005_race_18_and_over_virginia_counties.csv` | U.S. Census Bureau, 2000 census via the Census API (censusapi), every Virginia county | `2f6b9eaee0ab2230` | yes |
| `data/raw/us_census_bureau/2000/censusapi_dec_sf1_P008_hispanic_origin_by_race_virginia_counties.csv` | U.S. Census Bureau, 2000 census via the Census API (censusapi), every Virginia county | `04378eea4f87c678` | yes |
| `data/raw/us_census_bureau/2000/censusapi_dec_sf1_variables.csv` | U.S. Census Bureau, 2000 census variable labels via the Census API (censusapi) | `8d271cbac068d584` | yes |
| `data/raw/us_census_bureau/2010/censusapi_dec_sf1_P10_race_18_and_over_virginia_counties.csv` | U.S. Census Bureau, 2010 census via the Census API (censusapi), every Virginia county | `4a09c0c42a4b65c7` | yes |
| `data/raw/us_census_bureau/2010/censusapi_dec_sf1_P3_race_virginia_counties.csv` | U.S. Census Bureau, 2010 census via the Census API (censusapi), every Virginia county | `1ef02e11f54347ef` | yes |
| `data/raw/us_census_bureau/2010/censusapi_dec_sf1_P5_hispanic_origin_by_race_virginia_counties.csv` | U.S. Census Bureau, 2010 census via the Census API (censusapi), every Virginia county | `d921c7d547ff188c` | yes |
| `data/raw/us_census_bureau/2010/censusapi_dec_sf1_variables.csv` | U.S. Census Bureau, 2010 census variable labels via the Census API (censusapi) | `9f189f0de928345f` | yes |
| `data/raw/us_census_bureau/2020/censusapi_dec_pl_P1_race_virginia_counties.csv` | U.S. Census Bureau, 2020 census via the Census API (censusapi), every Virginia county | `a58780aed4b9c197` | yes |
| `data/raw/us_census_bureau/2020/censusapi_dec_pl_P2_hispanic_origin_by_race_virginia_counties.csv` | U.S. Census Bureau, 2020 census via the Census API (censusapi), every Virginia county | `e2a1d0d12226afd4` | yes |
| `data/raw/us_census_bureau/2020/censusapi_dec_pl_P3_race_18_and_over_virginia_counties.csv` | U.S. Census Bureau, 2020 census via the Census API (censusapi), every Virginia county | `16f730749ea042da` | yes |
| `data/raw/us_census_bureau/2020/censusapi_dec_pl_variables.csv` | U.S. Census Bureau, 2020 census variable labels via the Census API (censusapi) | `5ea0587ac950e254` | yes |
| `data/raw/us_census_bureau/population_of_states_and_counties_1790-1990_virginia.pdf` | U.S. Census Bureau, Population of States and Counties of the United States: 1790-1990 (forstall1996), title page and Virginia pages | `1c2ab9890f5666d3` | yes |
| `data/raw/va_dept_of_elections/county_board_2000-2026.csv` | Virginia Department of Elections, Historical Elections Database (vaelections), every County Board contest | `6cf331b77ed40237` | yes |
| `data/raw/va_dept_of_elections/president_1924-2024.csv` | Virginia Department of Elections, Historical Elections Database (vaelections), Arlington's presidential vote | `9a158acffa615df9` | yes |
| `data/raw/va_dept_of_elections/registration_2010-2025.csv` | Virginia Department of Elections, monthly Registration Statistics (varegistration) | `c153e1b1bcf8fb3a` | yes |

## Sources with no copy held

Cited, but neither filed in `documents/` nor held under `data/raw/`; the entry's `annotation` says why.

| key | author | date | title | url |
|---|---|---|---|---|
| census1880schedule |  | 1880 | 1880 U.S. Census, population schedule, Jefferson Township, Alexandria County, Virginia |  |
| vollin1974 |  | 1974 | George Vollin, Jr., et al. v. Mills E. Godwin, et al. |  |
| vollinelectoralboard |  | 1976-03-05 | George Vollin, Jr., et al. v. Arlington County Electoral Board and Cornelia B. Rose |  |
| bestebreurtje2017 | Bestebreurtje, Lindsey | 2017 | Built By the People Themselves: African American Community Development in Arlington, Virginia, From the Civil War Through Civil Rights | https://mars.gmu.edu/ |
| bestebreurtje2024 | Bestebreurtje, Lindsey | 2024-11-07 | Built by the People Themselves |  |
| hudson2026 | Hudson, Sally | 2026 | Personal knowledge of a serving Board member |  |
