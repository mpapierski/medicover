medicover
===

Medicover mobile app is useless. No reminders. No calendar integration. No location data.

This script downloads your medical appointments from Medicover site, and exports them to your CalDAV server. All your appointments are matched with up-to-date Medicover locations paired with geographic coordinates (thanks OpenStreetMap!). So you can just open your calendar, click on your appointment, click on the location and navigate there.

You can also write the appointments to an ICS file which can be imported to many calendar programs,
including Google Calendar ([by uploading a file](https://support.google.com/calendar/answer/37118)
or [by URL](https://support.google.com/calendar/answer/37100))

Very rough around edges (works for me (tm)). Quickly hacked together in one evening. Use at your own risk.

# How to use

## Set env vars:

### MEDICOVER_USERNAME

Your card number (or any other valid ID in your Medicover portal).

### MEDICOVER_PASSWORD

Password to your Medicover portal.

### CALDAV_URL

Address to your `CalDAV` server. (ownCloud, Google, etc.)

This script will use *Medicover* calendar in your `CalDAV` server. Please create it first before use.

Alternatively, you can use the `-o` command line argument to output the calendar to a file.

## Command line usage

1. Run `medicover.py` to extract your appointments. It will save them to `appointments.json`.
2. Export your appointments to one of the following targets:
  * Send the appointments to your `CalDAV` server
  ```
  python export.py -i appointments.json
  ```
  * Store the appointments in an ICS file.
  ```
  python export.py -i appointments.json -o appointments.ics
  ```

Note that if you provide both the CALDAV_URL environment variable and the `-o` argument,
the calendar will be sent to `CalDAV` and saved to a file.

```
usage: export.py [-h] -i FILE_NAME [-o FILE_NAME] [--caldav CALDAV_URL]
                 [-p NAME]

optional arguments:
  -h, --help            show this help message and exit
  -i FILE_NAME          Input JSON file with appointments
  -o FILE_NAME          Output ICS file
  --caldav CALDAV_URL   URL of the CALDAV server
  -p NAME, --person_name NAME
                        Name to append to calendar entries
```

## Locations

It is important that (if you do not use default `locations.json`) you should use `locations.py` script to extract new Medicover locations. If you care about your old data, you should check if Medicover location you used in the past still exists. If no, just add `"old location": null` to `locations.json`.

This script fuzzy-matches API downloaded appointment address, to names located presented on the website. Fuzzy matching is implemented because data from API does not equal data found on the main website.

## TODO

- Foreign timezones support (`Europe/Warsaw` is hardcoded in the code as CalDAV needs timezone aware dates; Medicover API seems to use only localtime (again, it has assumed `Europe/Warsaw` for .PL))
- Make it works on other Medicover portals (outside .PL)
- One script instead of two (three)
- Figure out scheduling (create new appointment straight in your special calendar), and cancellation (see rfc6638, it might be possible through some kind of simple web service that calls medicover api? does iOS support this?)
- Sharing your calendar entries or something 
- Update Medicover locations instead of overwrite to keep the database updated
- Send notifications (email, sms) when new appointment is added to your calendar

# Author

Michał Papierski <michal@papierski.net>

# Disclaimer

Medicover is owned and managed by Medicover Holding S.A., a privately-held company headquartered in Luxemburg.

I am not related with Medicover in any way.
