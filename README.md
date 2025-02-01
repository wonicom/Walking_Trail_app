# Air Quality App for Sports Enthusiasts

This app recommends optimal walking routes by utilizing real-time air quality data.
Based on the IQAir API, it analyzes real-time Air Quality Index (AQI), pollutant levels (PM2.5, PM10, ozone, etc.), and air quality forecasts to provide users with the cleanest and most comfortable walking paths.

## The API allows the app to :
  + Check real-time air quality for your current location or selected walking routes.
  + Get detailed pollutant information and predict future air quality changes.
  + Receive alternative walking route recommendations based on real-time data for cleaner air.

# Overview

The Air Quality App for Sports Enthusiasts is designed to help users stay informed about air quality while engaging in outdoor activities such as running, cycling, or hiking. The app provides real-time air quality updates along chosen routes and offers recommendations for alternative routes with cleaner air.

By integrating with GPS and air quality APIs, the app ensures that users can make informed decisions about their outdoor workouts, helping them avoid areas with high pollution levels. Additionally, users receive real-time alerts when air quality drops below safe levels, allowing them to modify their routes accordingly. The app also integrates with popular fitness tracking apps to combine workout performance data with air quality insights, creating a seamless experience for fitness and health-conscious individuals.

# Keyfeature

## Real-Time Air Quality Insights
 + Check real-time air quality data for your current location or selected outdoor routes.
 + Get detailed pollutant information (AQI, PM2.5, PM10, ozone, etc.).
 + Receive air quality forecasts to plan safer workout routes in advance.
## Smart Route Recommendations
 + Identify alternative walking or running routes based on real-time air quality data.
 + Avoid high-pollution areas and find the cleanest outdoor paths for your activities.
 + Ensure safer outdoor workouts with dynamic route suggestions based on air pollution levels.
## GPS & API Integration
 + Seamless integration with GPS for precise route tracking.
 + Access real-time air quality data from trusted sources like IQAir API & Seoul Open Data Plaza.
 + Sync with fitness tracking apps to combine workout performance with environmental data.

# User Stories
| User stories | Description | Estimate |
|:---|:---|:---|
| Documentation - API research | Design | |
| Documentation - System Architecture | Refer to the diagram | 1 hour |
| Documentation - Environment Details of the Proxy Server | <ul><li>The proxy server is configured using HAProxy 2.7.</li><li>SSL/TLS encryption is utilized to enhance security during data transmission through the proxy server.</li><li>All traffic logs are recorded in `/var/log/haproxy.log`, and server status is monitored via Prometheus.</li></ul> | 2 hour |
|Documentation -Queue Server| **Message Broker Software**<br>- Based on the AMQP protocol, utilizing queues, exchanges, and routing keys to distribute and manage messages.<br>- Used in **microservices** and **event-driven architectures**. <br><br> **Proxy to Queue Request Transmission** <br> - Ensures smooth communication when the proxy server sends data to the queue (request queue). <br><br> **Fine Dust Information for Seoul and Jeju** <br> - Retrieves one piece of fine dust information each for **Seoul** and **Jeju** from the queue. <br><br> **Sequential Transmission & Delay Testing** <br> - Sends the first request, introduces an intentional delay, and then sends the second request to verify whether the overall **flow** operates correctly.| 1 hours |
|Documentation - API Server | Language: Python <br> Linux Server: Ubuntu | 1 hours |
|Documentation - DB | Database Type & Version: MySQL 8.0 <br> Server Environment: Ubuntu 20.04 <br> Host: localhost <br> Port: Default (3306) <br> User: root | 30min |
|Documentation -Detail | 

