==============
Django GeoPoll
==============

App goals:

* Provide data for statistical analysis

	* Simple export formats for off-line presentation or analysis
	
	* Arbitrary metadata inclusion for questions, answers and users

* Pluggable ``User`` model settings

* Allow for offline geocoding

* Provide an API for remote voting (partner sites)

* Allow a flexible throttling mechanism for voting (User can vote only once, once a week, once a month, etc.)

* Questions have optional eligibility boundaries. Voters must reside within the boundary to vote.

