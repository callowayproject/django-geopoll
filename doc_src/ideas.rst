What is a Geographic Poll?
==========================

A geographic poll consists of at least a question and two answers (it's not much of a poll if there is only one answer). You may specify additional information such as:

* Start date and time
* End date and time
* Allow, Show or disable comments
* A boundary area in which the voter must reside to answer the question
* Key-value meta data

A publish date and a slug are is used to create a URL for the poll.
(possible: Custom name or URL for a poll instead of date-slug?)

Answers consist of the text of the answer as well as optional key-value metadata.

What does a Vote count?
=======================

The User model is flexible based on installation in the project. It will default to 'auth.User' unless otherwise set.

A vote will have a link to the question as well as a link to the answer chosen. The address string entered is stored for later or bulk geocoding. The longitude and latitude, the date and time voted, the day, month, year, hour minute as individual fields and the source of the vote.

Exporting vote data
===================

The exporting can include a set of boundary layers to tabulate the votes for each boundary. So you could export the voting data for a question and specify the state and county layers and the export would contain:

	{
		"user": "Sam Dalton", 
		"choice": 435, 
		"choice_text": "Abrams",
		"state": "MD", 
		"county": "Anne Arundel", 
		"source": "Facebook",
		"vote_datetime": "2011-12-31 13:23:00",
		"vote_year": 2011,
		"vote_month": 12,
		"vote_day": 31,
		"vote_hour": 13,
		"vote_minute": 23,
		"question_metadata": {"key1": "value", "key2": "value"},
		"answer_metadata": {"key1": "value", "key2": "value"},
		"user_metadata": {"key1": "value", "key2": "value"}
	}

Metadata Entry and Storage
==========================

There is one model for tracking all metadata. Metadata consists of just free-form key and value fields and the ubiquitous id field.

There are two methods of entering related metadata: inline (with or without auto-complete) and JSON.

Inline is the easiest, as it uses the standard Django inline admin class. Autocomplete is recommended to help with mistyping keys.

The JSON version is for a single line/field representation, or where you are editing metadata for an item from within an inline block. This converts all the current metadata into a JSON string, and on saving, converts the edited string to records.


Importing boundaries
====================

TBD. Investigate ChiTrib Boundaries

Creating a Poll
===============

#. Go to the GeoPoll admin and create a new GeoPoll.

#. Enter the question

#. If the poll doesn't start immediately, set a start date and time.

#. If you want the poll to end at a specific date and time, set it in the expire date and time fields.

#. Make sure the comment status is correct.

#. Optionally select a eligibility boundary. Voters must reside within this boundary to vote.

#. Enter in key-value metadata, if necessary, in the listing provided. They autocomplete from previous metadata entries for easier entry.

#. Enter in the answers and their metadata in the listing provided. The metadata will be a JSONField representation.