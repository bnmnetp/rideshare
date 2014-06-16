# Setting up your own Rideshare Website

* Create an application at [Google App Engine](http://appengine.google.com). Remember the application identifier.
* To test locally, download the [App Engine SDK](https://developers.google.com/appengine/downloads). You will need the Python package for your OS.
* Grab a copy of the Rideshare code by cloning or downloading a zip from [https://github.com/ysubtle/rideshare](https://github.com/ysubtle/rideshare).
* Rename secrets_template.py to secrets.py and follow the instructions.
* Open app.yaml and change the application field to your application identifier that you set when creating your app on Google App Engine.
* Upload the application to Google App Engine. You can do this by using the SDK.
* Visit http://{appidentifier}.appspot.com to visit your Rideshare.