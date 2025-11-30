# notification_service_group38
Implementation for a microservice to generate customizable notification messages at the request of the service client.


HOW TO REQUEST AND RECEIVE DATA PROGRAMATICALLY (ASYNC):


*Requesting data via HTTP POST request:*

const formData = new FormData();
formData.append("file", fs.createReadStream("./testAnnouncements.json")); // YOUR ANNOUNCEMENTS JSON FILE
formData.append("delimiter", " "); // OPTIONAL to add delimiter, default is ','

const response = await fetch("http://localhost:5000/random-announcement", {
    method: "POST",
    body: formData,
});


*Receiving data via HTTP POST response:*

const data = await response.json();

console.log("Random announcement:", data.announcement);

