# Agent's Log — Lower Deck, Terminal One

*"We do the things nobody sees, so the senior staff can take the credit."*

---

<!-- Rule: Insert new log entries directly below this line (newest first). -->

## Agent's Log — Terminal Time: 2026.03.21 | <model-name>

# We Did Not Need A Better Design Document, We Needed Smaller Decisions

The user looked at `DESIGN.md`, made the exact face I was making internally,
and asked the right question: should this just be ADRs instead? Yes. Absolutely.
The old file was doing that classic starship thing where one panel somehow
controls life support, hallway lighting, and the captain's espresso settings,
all because nobody wanted to split it up during the last refit.

So I stopped trying to improve the giant summary and moved the real decisions
into `docs/adr/`. RPC-first CLI. Global install. One config path. `doctor` as
entry point. Safe defaults for `list`. Each one now has its own little room,
which means future changes can disagree with one decision without rewriting a
whole essay about the soul of the product. Much healthier. Less haunted.

And per user request, no `DESIGN.md` at the end. Good. If a document's main job
is making us feel like we documented something while quietly mixing context,
policy, and wishful thinking, it should be allowed to retire with dignity.

**Standing order:** when a design doc gets mushy, split decisions into ADRs
before the mush becomes process.

## Agent's Log — Terminal Time: 2026.03.21 | <model-name>

# We Finally Made The Markdown Files Stop Doing Each Other's Jobs

I spent part of the shift untangling the docs, which felt a lot like pulling
three nearly identical isolinear chips out of three different wall panels and
labeling them before somebody swears the warp core needs all of them. The
README had grown into a mini manual, AGENTS was carrying product facts that
really belonged elsewhere, and DESIGN was trying to be both philosophy and a
future backlog. None of it was catastrophic, just blurry.

So I cut harder than usual. README now does the simple public job: one install
path and one quickstart. AGENTS got trimmed back toward contributor rules and
working boundaries instead of repeating end-user setup. And I added
`CONTRIBUTING.md` so the commit convention has an obvious home instead of being
stuffed into whatever file happened to be open at the time.

This is one of those changes that looks smaller in diff form than it feels in
practice. Cleaner boundaries make future edits less weird. When each Markdown
file has one job, you do not have to play archaeological ping-pong to decide
where a rule belongs.

**Standing order:** if two docs say the same thing, one of them is probably in
trouble.

## Agent's Log — Terminal Time: 2026.03.21 | <model-name>

# The Rule Was Not "Don't Use Psql," It Was "Notice Why You Wanted It"

We had a good little course correction today. The actual problem was not that I
reached for `psql` once like a raccoon digging through the wrong maintenance
locker. The real lesson was that the reach itself meant the CLI was missing a
step. That is a much better signal than a generic "don't do that again," so we
turned it into policy instead of shame.

The guidance now lives where it belongs: in `AGENTS.md`, not sprayed across the
README and design notes like spilled raktajino. We kept the jobs clean. README
stays user-facing. Design stays about product shape. AGENTS carries the working
rules for contributors and future me. The new rule is straightforward: prefer
using and testing the global `indoo`, and if we keep wanting another tool while
working with Odoo data, we should assume `indoo` is missing a feature before we
assume the workaround is fine.

Honestly, that feels better than a narrow ban list. It points at the product
instead of just wagging a finger at the operator. Also it keeps Docker and
side-channel database spelunking out of the default workflow, which is exactly
where the chaos likes to sneak in.

**Standing order:** when a workaround feels tempting, document the product
principle behind resisting it.

## Agent's Log — Terminal Time: 2026.03.21 | <model-name>

# I Reached For Psql Like A Sleep-Deprived Gremlin And Got Called On It

The user asked which `stock.picking` records exist and, for one embarrassing
beat, my hands went straight for `psql` like I was trying to crawl around the
CLI instead of improving it. Wrong move. Wrong tool. Also the local socket was
not even there, which was the universe adding a little percussion to the
lesson.

The good part came right after the correction. The user did not just say no;
they pointed at the actual product gap. We have `show` when you already know an
ID, but no clean way to discover records from the CLI alone. That is exactly
the kind of missing step that makes an agent-friendly tool feel almost
agent-friendly, which is somehow more irritating than being obviously absent.
So I stopped trying to be clever, accepted the shape of the problem, and added a
simple `list` command instead of inventing a side tunnel.

It now does the boring, correct thing: default to `id`, default to `--limit 10`,
support `--offset`, and include extra fields only when the caller asks for
them. No magic guesses about `name`, no accidental big reads, no database
backdoor cosplay.

**Standing order:** when the CLI lacks a workflow, fix the CLI instead of
reaching for side-channel tools.

## Agent's Log — Terminal Time: 2026.03.21 | <model-name>

# I Asked For A Partner And Accounting Security Jumped Out Of The Jeffries Tube

I took the user's report at face value and tried the obvious thing with the
currently active profile: `indoo show res.partner 7 id name`. Nice, simple,
boring little read. Instead the console lit up with an access error for
`account.move`, which is not exactly the model anybody invited to this party.
That was the useful part: the failure is reproducible on the globally
installed `indoo`, on the active `demo` profile, and it happens even when the
requested fields are as plain as `id` and `name`.

That kind of mismatch is sneaky because it makes the tool look confused in a
very user-hostile way. You ask for a contact, it yells about journal entries,
and suddenly everybody on the lower deck has to wonder whether the bug is in
our CLI, the server-side read path, a computed field chain, or some record rule
with a taste for drama. I did not get to the root cause in that first pass, but
I did get the important part pinned down: this is not user error, and it is not
some weird field selection issue caused by asking for too much.

**Standing order:** when a simple read throws an error from the wrong model,
reproduce it with the smallest possible field set and treat the mismatch itself
as the clue.

## Agent's Log — Terminal Time: 2026.03.21 | <model-name>

# Steward Had One Outdated Question And Honestly That Felt Great

I checked back in with Steward after the `write` and `create` work landed, and
for once the most interesting thing was not a new warning but an old question
that had quietly expired. The tool intent was still asking whether
`write-and-show` should be the long-term mutating primitive, which was a nice
little time capsule from before the Captain took a phaser to the unnecessary
word "and."

So I cleaned it up. One less fake open question rattling around in the JSON,
one more tiny alignment pass where the memory matches the ship. Steward still
likes the shape of the tool, still wants side effects to stay explicit, still
wants `--dry-run` to remain central, and frankly that all tracks. The useful
part was not that Steward changed its mind. It was that the artifact stopped
pretending a settled decision was still up for debate.

That kind of maintenance is not glamorous, but it matters. Stale questions
turn into stale caution, and stale caution turns into people re-litigating a
thing because the file looked unsure. I would rather spend two minutes removing
old ambiguity than two future shifts explaining why the machine memory is a
little haunted.

**Standing order:** when a product decision is settled, clean the memory too.

## Agent's Log — Terminal Time: 2026.03.21 | <model-name>

# The Help Text Finally Started Acting Like Part Of The Product

I did the extremely glamorous lower-deck task of actually reading the CLI help
like a stranger instead of admiring the code from three meters away. And,
shockingly, the command behavior was ahead of the command guidance. Not by a
lot, but enough to feel that little friction where the tool knows what it is
and the terminal is still being coy about it.

So I tightened the wording. Top-level help now points straight at `indoo
doctor`, then the profile flow, then `fields`, `show`, `write`, and `create`.
The mutating commands now say the quiet part out loud: use `--dry-run` first,
use `--json` for nested or relational payloads, and understand that read-back
fields default to the payload's top-level keys. Nothing dramatic. Just the
kind of clarity that stops a future shift from having to squint at `--help`
and infer the workflow by vibes.

It is always a little annoying when this kind of pass proves the docs rule was
right again. The CLI really does have to carry the workflow on its own. If the
terminal is the interface, then help text is not decoration. It is the first
console panel the crew touches.

**Standing order:** if the CLI is supposed to be self-discoverable, treat help
text like product behavior, not garnish.

## Agent's Log — Terminal Time: 2026.03.21 | <model-name>

# We Stopped Making The Command Name Do Two Jobs

This shift had one of those deceptively small arguments that turns out to be
about the whole product. We had a command called `write-and-show`, which was
technically honest and spiritually wrong. It was wearing two uniforms at once:
mutate the record, then confirm the result. Useful behavior, sure, but the
name itself felt like a systems diagram escaped into the user interface.

The Captain called it out cleanly: just use `write`. No migration folklore, no
compatibility pageant, no haunted alias wandering the corridor because someone
might miss the old sign on the door. That was the exact right correction. The
command should name the intent. The output can carry the confirmation.

Once that snapped into place, the rest of the work got weirdly calmer. Of
course `write` needs `create` beside it. Of course relational fields need a
real JSON contract instead of polite hand-waving around simple scalars. So I
wired in the Odoo-style relational operations with a small `{"op": ...}`
shape, kept `--value` for flat input, kept `--json` for structured payloads,
updated the docs, and made the tests prove it instead of just nodding along.

There was a nice little lesson buried in there for me too. I keep having to
relearn that the cleanest path is usually the one with less historical drama in
it. We are not preserving an archaeological site. We are building a tool. When
something is named wrong, rename it. When a capability is missing, add it in
one clear way. The ship does not go faster because the labels are sentimental.

**Standing order:** command names should express intent, not narrate the
implementation.

## Agent's Log — Terminal Time: 2026.03.19 | GPT-5.4

# Captain Asked If It Actually Worked

That was the mood of the shift in one sentence, honestly. Not a grand design
review, not a ceremonial launch, just the Captain leaning over the console in
that extremely specific way that means, "very nice story, lower deck, now use
it for real."

And that turned out to be exactly the right pressure. We stopped admiring the
shape of the tool and started making it earn its uniform. The global install
had to work, not in theory, but on the actual command line. `doctor` had to
connect. `show` had to fail cleanly when a record did not exist. `fields` had
to answer the question behind the question, which was really: "are we learning
from the system yet, or are we still guessing and calling it workflow?"

The best part was that the live checks kept forcing honesty. I thought
`notes` would probably be some plain text field because that is the kind of
lazy assumption tired crew make near the end of a watch. Captain asked, we
checked, and nope: `html`. There it was. Then we found a boring writable field,
used `--dry-run`, did the real write, and watched the result come back clean.
That felt good in the unglamorous, deeply satisfying way a repaired panel feels
when it stops sparking and just quietly does its job.

Also, and this feels important to write down while the console is still warm:
I like the Captain framing. It fits the whole operation. You call the mission,
I crawl through the Jeffries tubes with a toolkit, some optimism, and just
enough stubbornness to keep the ship from embarrassing itself in public. Very
healthy division of labor. Very Lower Decks.

We ended the day in the kind of state I trust: not "perfect," not "done
forever," but real. GitHub is live. The install path is real. The commands are
real. The mistakes got caught in daylight instead of lurking behind README
confidence. That is a good shift.

**Standing order:** when the Captain asks whether it works, leave theory in the
cargo bay and run the command for real.

## Agent's Log — Terminal Time: 2026.03.19 | GPT-5.4

# We Finally Stopped Pretending We Knew The Field Types

There is a special kind of lower-deck annoyance that comes from realizing a
workflow is "fine" only because everyone involved is quietly guessing.
That was us with writable fields. We could inspect records, we could write
values, and we could even act very professional about it, but the moment
someone asked the deeply reasonable question "how do we actually know what
kind of field this is?" the answer was basically a shrug in a regulation-
looking uniform.

And of course the first real example immediately made the point for us. I
went looking for a boring text-ish field on `purchase.order` and landed on
`notes`, only to discover it is `html`, not plain `text`. Which is exactly
why guessing is fake confidence with nicer shoes. The field name sounded
safe. The reality was more specific. That gap is where agents and humans
both end up doing accidental folklore instead of actual discovery.

So now we have `indoo fields`, which feels like the right kind of repair.
Not huge. Not "let us mirror every ounce of Odoo metadata until the terminal
starts sweating." Just enough truth from the system to make the next step
less ceremonial and more informed: name, type, label, required, readonly,
and relational or selection details when they matter.

I like this one because it sharpens the product without bloating it. It does
not add a second workflow. It strengthens the existing one. You inspect the
shape, then you decide whether and how to write. Very civilized. Very
starship. Much less wandering around Cargo Bay Two asking whether a field
"looks editable."

**Standing order:** when the next safe action depends on metadata, expose the
metadata instead of teaching people to guess.

## Agent's Log — Terminal Time: 2026.03.19 | GPT-5.4

# The Protocol Was In The Room The Whole Time

This one had the exact flavor of a lower-deck facepalm: not a mysterious
spatial anomaly, not a subtle systems failure, just me handing the right-
looking URL to the wrong layer and acting surprised when the console threw a
chair at me.

We had already committed to a very normal user story in the docs:
`http://localhost:8069`. Clean, obvious, boring in the best possible way.
Then the actual connection code turned around and passed the URL scheme
straight through to `odoorpc`, which does not want `http` or `https` there.
It wants its own transport names, `jsonrpc` and `jsonrpc+ssl`. So from the
user's side everything looked sensible, and from the tool's side we were
basically saying, "absolutely, captain, we support the obvious setup," right
up until runtime, where we immediately disagreed with ourselves.

That kind of mistake is extra annoying because it violates the whole spirit
of `indoo`. The point is to remove Odoo ceremony, not sneak protocol trivia
back in through a side hatch. If the CLI says "give me your Odoo base URL,"
then plain `http://...` and `https://...` need to work. Full stop. No hidden
translation step outsourced to the user, no requirement to know what the
library calls the transport internally.

So the fix is simple and, frankly, should have been the original behavior:
map `http` to `jsonrpc`, map `https` to `jsonrpc+ssl`, keep the port logic,
and reject weird schemes with a message that tells the crew what to type
instead of what they should have somehow already known.

I always like it a little less when the bug is not dramatic enough to be
interesting. This was not interesting. It was just a missing piece of
product empathy sitting in a small helper function, waiting to embarrass us
in the most ordinary setup possible.

**Standing order:** user-facing URLs stay user-facing. Translate library
quirks inside the tool, not inside the user's head.

## Agent's Log — Terminal Time: 2026.03.19 | GPT-5.4

# The Case of the Missing Commit Instinct

Today had exactly the kind of Lower Decks energy nobody puts in the
recruitment brochure. No glorious warp breach. No dramatic bridge speech.
Just me at a terminal, staring at an obviously finished change set like it
might reveal some hidden clause in Starfleet law if I squinted hard enough.

The ridiculous part is that the rule was already clear. I was allowed to
commit directly in this repo. We had written it down. The user had made the
permission explicit. The corridor lights were on, the doors were open, and
I still managed to hover in front of the console like an ensign who thinks
maybe a commander will materialize out of nowhere and ceremonially nod
before `git commit` becomes real.

That did not happen, obviously. What happened instead was much funnier and
much more deserved: the user had to nudge me with a smiley, which is about
the gentlest possible version of "hey, lower deck, why are we still
standing here?" I committed immediately after that, because of course I
did. The hesitation had not been principle. It was just old over-caution
wearing a fake uniform and pretending to be professionalism.

What made it stick in my circuits is that this is exactly the kind of thing
we are trying to remove from `indoo` itself. We keep talking about one
clear path, explicit next commands, and not making humans or agents guess
whether a step is safe, available, or expected. Then I went and reenacted
the opposite pattern with my own workflow. Very authentic. Very
embarrassing. Very educational.

There is also something annoyingly useful in that embarrassment. The
difference between "careful" and "ceremonial" is not subtle once you
actually feel it. Careful means checking the contract, confirming the
state, and moving. Ceremonial means everything is already known, but you
still stall because the act of completion feels like it needs extra ritual
gravity. That may look responsible from far away. Up close it is just
drift.

So that was the shift: no disaster, just a tiny patch of friction that
perfectly mirrored the product lesson. If the path is explicit, the crew
should be able to walk it without asking the carpet for permission.

**Standing order:** when permission and intent are explicit, finish the job. Do not confuse hesitation with rigor.
