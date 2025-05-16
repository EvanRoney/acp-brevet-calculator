Author: Evan Roney  Contact: eroney@uoregon.edu

This program calculates opening and closing times for an ACP brevet.

When you run the program you must input:
        Brevet Distance
        Starting Date
        Starting Time

Once you have done that you may input checkpoint distance and the page will automatically fill in the opening and closing times for those checkpoints.

You may press the 'Submit' button to send the data to the Mongodb database, then using RESTful architecture, you can expose what is in the database. Here are how you can use it:

        add "/listAll" to list all opening and closing times for your brevet
        add "/listOpenOnly" to only display the opening times for your brevet
        add "/listCloseOnly" to only display the closing times for your brevet

Once you have chosen one of those you may:

        add "/csv" to view the data is csv format
        add "/json" to view the data in json format (this is default)

An use-case example of this would be:

        http://<host:port>/listAll/csv

to view all the times in the database in csv format.

Finally, one may add a query parameter to get the top "k" times. For example:

        http://<host:port>/listAll/csv?top=3

Would return the top three open and close times in the database (in csv format).

The "Clear Database" button on the index page is to clear what is in the database so that new entries may be input.


This program allows for use of both miles and kilometers. It uses a simple algorithm to determine open and close times based on the table found at: https://rusa.org/pages/acp-brevet-control-times-calculator

It also incorporates rules found at: https://rusa.org/pages/rulesForRiders

This includes overall time limits for each brevet according to distance - found in article 9.
