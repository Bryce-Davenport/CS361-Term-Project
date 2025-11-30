import express from "express";
import multer from "multer";
import fs from "fs";

const app = express();
const upload = multer({ dest: "uploads/" });

let visited = new Set(); // saves visited indices

app.post("/random-announcement", upload.single("file"), (req, res) => {
  try {
    const filePath = req.file.path;
    const delimiter = req.body.delimiter || ",";
    const data = JSON.parse(fs.readFileSync(filePath, "utf8"));

    let announcementArr = [];

    if (Array.isArray(data.announcements)) {
      // if announcements are in an array
      announcementArr = data.announcements.map(a => a.trim()).filter(a => a.length > 0);
    } else if (typeof data.announcements === "string") {
      // if announcements are a string separated by delimiter
      announcementArr = data.announcements
        .split(delimiter)
        .map(a => a.trim())
        .filter(a => a.length > 0);
    } else {
      throw new Error("JSON needs an 'announcements' array or a delimited string");
    }

    // generate random index, checks if index has been used before
    if (visited.size === announcementArr.length) {
      visited.clear();
    }
    let index;
    do {
      index = Math.floor(Math.random() * announcementArr.length);
    } while (visited.has(index));

    visited.add(index);

    const randomAnnouncement = announcementArr[index];
    res.json({ announcement: randomAnnouncement });

  } catch (error) {
    console.error("Error:", error);
    res.status(500).json({ error: "Failed to process announcements" });
  }
});

app.listen(5001, () => {
  console.log("Random Announcement Microservice running on http://localhost:5001");
});
