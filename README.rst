1. Go to `http://appengine.google.com <http://appengine.google.com>`_
and create a account with the website.

a. You will be able to use an existing Google account.

2. After successfully logging in, click the “Create Application” button
on the screen

a. Follow the verification process to create your application. You will
be asked to pick an Application Identifier and an Application Title. Any
other selections can be left at the default options.

i. Remember the Application Identifier; you’ll need it later

b. Upon successfully creating the application, click the “dashboard”
link.

3. Next download the Google Appengine Launcher from
`https://developers.google.com/appengine/downloads <https://developers.google.com/appengine/downloads>`_.

a. Be sure to pick the correct version for your operating system under
the “Google App Engine SDK for Python”

b. Install the download, keeping all the default values.

c. DOWNLOAD PYTHON?

4. Next you need to check out a copy of the code from our repository.

a. Go to
`https://bitbucket.org/bnmnetp/rideshare/downloads <https://bitbucket.org/bnmnetp/rideshare/downloads>`_

b. Download the “rideshare.zip” file

c. Extract the file contents

5. Now that you have the code, its time to make the necessary changes to
the code in order to match your school.

a. In the “src” folder of the downloaded files, open “nateusers.py” in a
text editor.

i. In the “class LoginHandler(BaseHandler)” section of the file, locate
the line “ if ‘Luther College’ in schoollist”. In this line you must
replace “Luther College” with the name of your university as it appears
on your university’s Facebook page. This ensures that only users from
your school can use the website.

ii. In addition, you must create a Facebook App for your Rideshare
website.

1. Go to
`http://developers.facebook.com <http://developers.facebook.com>`_

2. In the top toolbar, click on “Apps”

3. In the upper right corner, click “Create New App”

4. Give your app a name, and hit Continue.

5. After continuing through the remaining screens, you will be brought
to the admin page for your new application

6. Click the “Website with Facebook Login” section, and input
“http://APPLICATIONIDENTIFIER.appspot.com” (without quotes) into the
“Site URL” space, using the Application Identifier we got in step 2 in
place of “APPLICATIONIDENTIFIER”

7. Click Save Changes

8. Now the application is complete. Keep this page open, as you will
need the “App ID” and “App Secret” found at the top of this page

iii. Copy the “App ID” and “App Secret” values from the Facebook App
page into the “nateusers.py” file. You can find the “FACEBOOK\_APP\_ID”
and “FACEBOOK\_APP\_ SECRET” values towards the top of the file.

iv. Save this file and exit

b. Next, locate the “app.yaml” file within the “src” folder and open it
in a text editor.

i. The first line should be changed to read “application:
YourApplicationIdentifier”, supplying your appengine Application
Identifier from step 2 as the “YourApplicationIdentifier” value.

ii. Change line 2 to read “version: 1”

iii. Save this file and exit

c. Next, locate the “main.py” file within the “src” folder and open it
in a text editor.

i. Find the line towards the top of the file that starts with “college =
College(name…)

ii. Replace all the values for Luther College with values that match
your university. For lat and lng, we recommend finding the values using
`http://itouchmap.com/latlong.html <http://itouchmap.com/latlong.html>`_
as a free service.

iii. Once again, use the AppID and Appsecret values from the Facebook
Application page.

iv. Save the file and exit

d. Within the “src folder, open the “static” folder”. Next, locate the
“functions.js” file within the “static” folder and open it in a text
editor.

i. Find the line starting with “var mycollege = new…”

ii. On this line, replace the values for Luther College with the values
for your own school. The order should be school name, school address,
latitude, and longitude. Be sure there is a comma between each value.

iii. Save the file and exit.

6. Open up the Google App Engine Launcher, and select your application.
On the top bar of the Launcher, select deploy. You may be prompted to
enter your login credentials from the website in step 1. This should
deploy your application to the website!

7. In your browser, navigate to
`http://APPLICATIONIDENTIFIER.appspot.com <http://APPLICATIONIDENTIFIER.appspot.com>`_,
with “APPLICTIONIDENTIFIER” replaced with the Application Identifer from
step 2. You should now be able to log in to your website and begin!


