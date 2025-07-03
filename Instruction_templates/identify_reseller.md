**Context**
Now we have built the Liberty cleaning process and its working.

But since there is 5-6 more resellers reports to parse and clean, we need to set up a structure to identify what reseller it is. 
Since this is going to work mainly with an HTTP request, we need to set up some sort of trigger in the beginning which "cleaner" we should use. 
Lets say that we have an "identify-script" and this identifies which the resller is, if it for example identify that its reseller:"Liberty" - it should trigger the Liberty cleaning and parsing, since that document looks different to the rest. 

Here is a list of the resellers available today:
Liberty
BOXNOX
Skins NL
Creme de la creme
Galilu
Aromateque
Skins SA
Selfridges


So the first thing the system needs to do is to identify which reseller it is, then trigger that specfific code.

What is the best way for me to hand you information about how the document looks like? In order for you to fetch the correct document.