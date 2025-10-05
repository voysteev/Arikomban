Detects wild animals using a YoloV8s finetuned model.
Store the pictures taken in s3 bucket(AWS).
A database of (animal class, timestamp, location, link to the pic in s3 bucket) is maintained using RDS(AWS).
A website for tourists to ckeck any wild animal detection around a particular area within a distance of 10KM (uses Haversine Formula).
A telegram bot that sends alert to the locals with a picture and warning msg.
