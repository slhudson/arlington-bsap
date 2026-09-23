# Setup

Paste this whole file into a new Claude conversation. It tells Claude what you
are setting up and how to help. Written for Alex; it works for anyone joining
the project.

If you're reading this as an email attachment, that's expected — the repository
is private, so the first copy has to arrive outside it.

---

I'm working on a research project with a collaborator who has moved our shared
files into a GitHub repository. I need to get set up so I can edit the figure
code on my own machine. Please walk me through it one step at a time, waiting
for me to confirm each step worked before moving to the next. Ask me what
operating system I'm on before giving any commands.

## What the project is

Arlington County's Board Structure and Performance study. Five figures in
matplotlib, built from census volumes, the county's election records and a
historical roster of the County Board. The figures aren't finished — I'll keep
editing them — which is why I need this working locally rather than just
reading the output.

## What changed

The scripts, the source documents and the paper now live in one private GitHub
repository, `slhudson/arlington-bsap`. The figures rebuild from the committed
sources with a single command instead of being regenerated and re-uploaded by
hand. The repository is connected to Overleaf, so the paper pulls the figures
the pipeline produces.

## How the repository is organised

    fetch/        downloads a published source into data/raw/ (run on demand)
    transcribe/   reads scans into data/transcribed/ (run on demand)
    build/        turns data/raw/ and data/transcribed/ into data/clean/
    analysis/     one script per figure, reading only from data/clean/
    data/         raw/ (as published), transcribed/ (read off the scans,
                  or hand-keyed under by_human/), clean/ (built)
    figures/      pdf/ for the paper, png/ for slides
    paper/        the LaTeX source, synced with Overleaf
    docs/         open questions, sources, figure rationale
    run.sh        rebuilds everything from the committed files

Two rules worth knowing before I touch anything. `data/raw/` and
`data/transcribed/by_human/` are never edited — they're the sources as
received. And decisions that change what a number *is* belong in `build/`,
while `analysis/` only decides how a number is shown; the analysis scripts
have no path to anything above `data/clean/`, so that separation is enforced
rather than just agreed. The README has a table of which script writes which
file.

## What I need to end up with

1. **A GitHub account.** I may already have one. I need to send my username to
   my collaborator so she can add me to the private repository — cloning will
   fail until she has, so this is the first thing to sort out.
2. **Git installed**, and signed in to GitHub.
3. **Claude Code installed and working.** This is Claude running in my terminal
   rather than the browser, so it can edit the files directly instead of me
   downloading and re-uploading attachments. It needs a paid Claude plan.
4. **Python with pandas, matplotlib and openpyxl**, in a virtual environment
   inside the repository folder. The project expects it at `.venv`.
5. **A successful build.** Running `bash run.sh` from the repository should
   print a build step, then five figures, then a line about `figures/pdf` and
   `figures/png`. That's the test that everything works.

## How I'd like you to help

Go one step at a time. Tell me what to type, what I should see if it worked,
and what to do if I see something else. Don't assume I know git — explain what
a command does before I run it, briefly.

If a step needs something only my collaborator can do, say so plainly and tell
me what to send her, rather than trying to work around it.

Once `bash run.sh` works, stop there. From that point I'll switch to Claude
Code inside the repository folder, and ask it to help me with the figures.

## The first thing I'll want to do afterwards

Change something small in a figure and rebuild, to see the loop work end to
end. `analysis/` has one script per figure, each named for the figure it
produces. `analysis/style.py` holds the colours and fonts they all share.
