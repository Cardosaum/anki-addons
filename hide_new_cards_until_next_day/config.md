# [HIDE NEW CARDS UNTIL NEXT DAY](https://ankiweb.net/shared/info/1999327581)

Disclaimer: This is my first addon and is by no means free of bugs, please keep in mind that undesired behavior can happen. I'd suggest to backup your collection frequently.

## ADDON OPTIONS

Currently this addon supports two possible hide options:

1. Hide *all* new cards until tomorrow
2. Hide *only* new cards **added today** until tomorrow

You can configure the default behavior modifying the option `"added_today_only"`.

If this option is `"false"` (the default), then the first behavior listed will
take place. If `"true"`, then the second will.

## HOW THIS ADDON WORDS?

It's function is basically the following:<br/>
First we find all new cards (issuing a query like: "is:new -is:suspended"),<br/>
Then we hide all the found cards (respecting the option `added_today_only` mentioned above).<br/>
We need to mark somehow which cards were suspended by this extension, so we are able to unsuspend them.<br/>
In order to achieve this, we add a tag in this format to each suspended card: "`ø::hide_new_cards_until_next_day::[hidden_at,redeem_at]::<year>-<month>-<day>`".<br/>
Due to this usage of tags you may experience an accumulation of "`ø::hide_new_cards_until_next_day::X`" tags. You only need to click in 'Tools > Check Database'<br/>
to get rid of the unused ones.<br/>
<br/>
BTW, just as a side note: if you are curious about why I chose to use such a 'excentric' tag format, consider that the character `ø` is one of the last chareters in the sort order, so the tags created by this addon will show up only at the bottom of the browser. And, if you didn't already get the `::` thing, just look at [this addon](https://ankiweb.net/shared/info/594329229) ;)<br/>

## WHEN THIS ADDON IS EXECUTED?

This addon has 3 triggers and 1 menu button.

1. It's automatically triggered during Anki startup;
2. It's automatically triggered every time you update the config file on the left when pressing '`OK`';
3. It's automatically triggered every time you add a new card;
4. It can be triggered via '_Tools > Hide new cards until next day_'.

