# gordias
Tool to gather contact information of public available sources.
TODO...


(Importing the abstract class from the folder above is a bit tricky -> see README file)
If you plan to overwrite the constructor of the abstract class in the subclass make sure to pass first\_name, last\_name and organization and set these as class variables (see source\_class.py).

\subsection{Matching of right user}
%TODO Describe what we just used in the two sources we have and mention the similarity function
What if there is no organization/company field and there are multiple persona as a result of an API request?
What if an organization/company field exists but it's None for every person in the list?
If either of the field is None then we go throught the person list and check the similarity for first and last name, if only for 1 person the similarity of first and last name is above 0.9 then we return this person, if there multiple persons match this criteria we can't tell for sure which person is the right one and therefore return nothing.


\subsection{Phrase similarity calculation}
%http://nlpforhackers.io/wordnet-sentence-similarity/



Country code to country name
% https://github.com/TuneLab/pycountry-convert

Nameparser
%https://github.com/derek73/python-nameparser

Locationparser
%https://geotext.readthedocs.io/en/latest/readme.html
%https://github.com/elyase/geotext


\begin{lstlisting}[language=Python]
field_list = ["contact_id", "first_name", "last_name", "email", "city",
	"country", "keywords", "twitter_url", "crunchbase_url", "xing_url", 
	"linkedin_url", "facebook_url", "profile_image_urls", "homepage", 
	"job", "orga_name", "orga_city", "orga_country", "orga_homepage", 
	"orga_crunchbase_url", "last_sync", "sync_interval"]0
\end{lstlisting}

If you add a new source delete both matrices so they can be created new(\&correctly) at the next start.

Google translator: https://github.com/ssut/py-googletrans
