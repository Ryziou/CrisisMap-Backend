<h1 align="center">CrisisMap</h1>

## Description

CrisisMap is a global disaster tracking and commentary application built to visualize humanitarian crises and enable user engagement through map-based insights. The app fetches real-time disaster event datra from an API by ReliefWeb, it displays an interactively visual map by using Mapbox. Each event can be explored in detail through a dynamic sidebar that includes disaster metadata and a comment system where authenticated users can post, edit, and delete their thoughts.

The application supports full user authentication, including account registeration, profile editing, and account deletion. Comments are permission-controlled so users can only modify or remove their own input. The homepage features a dashboard with data-driven visualizations such as a line, bar, radar, and pie charts. These provide insights into trends like disaster frequency, type distribution, and affected regions over time.

This was created by using React, JavaScript, CSS, Django REST Framework, PostgreSQL, Mapbox GL JS, Recharts, React Router, Axios, ReactMarkdown, Remark-GFM, HeadlessUI, and Heroicons.

Front-end: https://github.com/Ryziou/CrisisMap-Frontend 
Back-end: https://github.com/Ryziou/CrisisMap-Backend


## Deployment link

[Click here to try out the CrisisMap website!](https://crisismap.netlify.app/)

## Getting Started/Code Installation

1. Clone the front-end and back-end repository to your local machine. 
2. Open VSC with the folder as a main in terminal and split the terminals into two. 
    - One with the front-end and one with the back-end.
        - On the front-end, input "npm run dev" into it.
        - On the back-end, input "python manage.py runserver" into it.
3. Add a .env file to the front-end and add this key "VITE_API_BASE_URL=http://localhost:8000/api".
4. Open up your web browser and go to http://127.0.0.1:5173/ to start trying it out.


## Timeframe & Working Team (Solo/Pair/Group)

This project started on 04/06/2025 and It was completed on 12/06/2025.


## Technologies Used

### Front End
    - React
    - React Router
    - Mapbox GL JS
    - Recharts
    - ReactMarkDown + Remark-GFM
    - CSS
    - JavaScript
    - Axios
    - HeadlessUI
    - Heroicons

### Back End / Development Tools
    - Packages (django, psycopg2-binary, autopep8, pylint, djangorestframework, django-environ, djangorestframework-simplejwt, django-cors-headers, requests, whitenoise)
    - Django
    - Django REST Framework
    - PostgreSQL (hosted on Neon.tech)
    - ReliefWeb API (via proxy integration)
    - JWT Authentication
    - Django serializers and permissions (custom logic for ownership + comments)
    - Visual Studio Code
    - Git & GitHub
    - Windows Subsystem for Linux (WSL) with Ubuntu
    - Zsh (Z Shell) + Oh My Zsh
    - Node.js & npm
    - Postman (for API testing)
    - Vite
    - Python & pip

### External websites used for researching or use

#### Researching

[Google](https://www.google.com/)  
[MDN Web Docs](https://developer.mozilla.org/en-US/)  
[Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/index.html)  
[Mapbox](https://www.mapbox.com/)  
[Recharts](https://recharts.org/en-US)   
[React](https://react.dev/reference/react)  
[React Router](https://reactrouter.com/home)  
[HeadlessUI](https://headlessui.com/)  
[Heroicons](https://heroicons.com/)  
[Netlify for Front-end Hosting](https://www.netlify.com/)  
[Heroku for Back-end Hosting](https://www.heroku.com/)  
[ChatGPT for Seed DB](https://chatgpt.com/)  


## Brief

### MVP (Minimum Viable Product)

* **Build a full-stack application** by making your own backend and your own front-end
* **Use a Python Django API** using Django REST Framework to serve your data from a Postgres database
* **Consume your API with a separate front-end** built with React
* **Be a complete product** which most likely means multiple relationships and CRUD functionality for at least a couple of models
* **Complex Functionality** like integrating a 3rd party API or using a particularly complex React Component would mean that the CRUD and multiple relationships requirement can be relaxed, speak to your instructor if you think this could be you.
* **Implement thoughtful user stories/wireframes** that are significant enough to help you know which features are core MVP and which you can cut
* **Have a visually impressive design** to kick your portfolio up a notch and have something to wow future clients & employers. **ALLOW** time for this.
* **Be deployed online** so it's publicly accessible.



## Planning
<details>
    <summary>Wireframes</summary>
Main

![CrisisMap Whole Wireframe](https://res.cloudinary.com/dit5y4gaj/image/upload/v1749671641/115bf296-6415-4825-839b-d44de1483673.png)

Google Doc

[API Routing table document](https://docs.google.com/document/d/1Rr0VBVUDkZw6NwhyMg9lTs_xjYNe33ibLynYE9siJCQ/edit?usp=sharing)

ERD

![Models/Schemas ERD](https://res.cloudinary.com/dit5y4gaj/image/upload/v1749671777/fcd35df2-c380-43b4-949d-053e64934ae6.png)


</details>

## Build/Code Process

### Proxy Integration with External ReliefWeb API
A key challenge in this project was working with the ReliefWeb API. I started with creating a Django-based proxy endpoint that transforms a bunch of queries into valid ReliefWeb-compatible requests, which also uses a custom field filtering and sorting by latest.

```py
@api_view(['GET'])
def reliefweb_disasters(request):
    query = {
        'fields': {
            'include': [
                'id',
                'name',
                'status',
                'primary_country',
                'country',
                'primary_type',
                'type',
                'url',
                'date',
                'description'
            ]
        },
        'limit': 500,
        'sort': ['date:desc']
    }

    response = requests.post(
        'https://api.reliefweb.int/v1/disasters',
        json=query
    )
    return JsonResponse(response.json(), safe=False)
```
This proxy allows the frontend to achieve query parameters as if it were querying a local database. I'm very proud of this and I will now lead onto my 2nd proxy API that was built specifically for the home page.

### Complex Proxy Integration for Data Aggregation
The 2nd proxy API was very tough to make. One of the most technically interesting parts of this project was designing a Django-based proxy that not only forwards these requests, but also aggregates and transforms the data for frontend use in charts and stats.

```py
@api_view(['GET'])
def reliefweb_stats(request):
    total_query = { 'limit': 0 }
    total_data = get_reliefweb_stats(total_query)
    total_disasters = total_data.get('totalCount', 0)

    active_query = {
        'limit': 0,
        'filter': { 'field': 'status', 'value': 'alert' }
    }
    active_data = get_reliefweb_stats(active_query)
    active_disasters = active_data.get('totalCount', 0)

    recent_query = {
        'limit': 1,
        'sort': ['date:desc'],
        'fields': { 'include': ['name', 'status', 'date', 'primary_country', 'primary_type'] }
    }
    recent_data = get_reliefweb_stats(recent_query)
    recent_disaster = recent_data['data'][0]['fields']

    # More transformations: most common types, top countries, status counts, and monthly trends...
```
This endpoint powers much of the CrisisMap dashboard. I use it to:
- Fetch total and active disaster counts
- Identify the most recently reported disaster
- Count disaster types and statuses using Python's built in Counter syntax
- Group disasters by month for a historyical timeline line chart.

### Sidebar Integration with Mapbox
The interactive map sidebar was designed to replicate the feel of Google Maps' one. Clicking a pin would reveal detailed disaster information and a comment thread regarding it. With thanks to HeadlessUI's tab components, I created a flexible sidebar system that conditionally renders tabs and ties directly into the global disaster data.

```jsx
<SidebarTab
  disaster={selectedDisaster}
  onClose={() => setSelectedDisaster(null)}
/>

// SidebarTab.jsx
<TabGroup>
    <TabList>
        <Tab>Details</Tab>
        <Tab>Comments</Tab>
    </TabList>
    <TabPanels>
        <TabPanel>
            {disaster.title}
            {capitalizedStatus}
            {disaster.type}
            {dateEvent}
            {dateCreated}
            {dateUpdated}
            {country}
            {affected}
            <ReactMarkdown>{disaster.description}</ReactMarkdown>
    </TabPanel>
    <TabPanel>
      <Comments eventId={disaster.id} />
    </TabPanel>
  </TabPanels>
</TabGroup>
```
I'm happy about how this turned out and allowed users to interact with the dynamic content without leaving the map view. With ```@headlessui/react```'s tabs, I can enable state-driven rendering and use ReactMarkdown to format the description from ReliefWeb text.

## Challenges
### API Overload
As discussed above, it will still count towards a challenge honestly. It was one the of the biggest hurdles in this project whn trying to work with the ReliefWeb API. At first glance, it looked straightforward but then I quickly learned that it wasn't that easy. I ran into a lot of trouble trying to make queries in Django but then I eventually got one working.

```py
query = {
    'limit': 10,
    'sort': ['date:desc'],
    'fields': {
        'include': [
            'primary_type', 
            'primary_country', 
            'status', 
            'date']
    }
}
```
Once I was finally receiving structured data, I learned that the best way to analyze it was by using ```collections.Counter``` which helped me sort disaster types, monthly trends and common countries affected for the use of Recharts.

### Mapbox Madness
Mapbox is great. I created my very first one (thanks to the tutorial haha) really fast but then... I kept stumbling into issues. I wanted to feel intuitive like Google Maps where the user can just click on a marker, a side bar slides in and they can toggle between the details/comments. Sounds easy right?

At first it was easy. Pop markers down and that's it, just got to work hard on the sidebar but then I realised that there are some markers that are STACKING on top of eachother so the user won't be able to see all of them, only one.

So I tried to make it based on a boundary system, where the user can navigate the map and the results will pop in when you get close... but sadly this isn't right for ReliefWeb API as they use the same coordinates (lat/lon) for every humanitarian that has happened in a country. 

I then moved onto a possible action where we can use the cluster system. It will cluster the markers up so they can at least know how many are happening in that country. This was very hard as it honestly never worked. I eventually got them to work but then nothing responded the way I expected. Sometimes I clicked a cluster and it zooms way too far in making the markers very very tiny or times where clicking on an event broke the map because the sidebar didnt trigger.

Once I cracked it down and finally got it working, the biggest problem was the markers. I kept trying different math syntaxes to somehow randomize their location based on where they reside and had a tough time but I finally finished it.

```jsx
function spreadMarkers([lon, lat], index) {
    const spreadAmount = 0.1 + Math.random() * 0.1
    const angle = (2 * Math.PI * index) / 10
    return [
        lon + Math.cos(angle) * spreadAmount,
        lat + Math.sin(angle) * spreadAmount
    ]
}
```
This little baby nudges overlapped coordinates slightly apart in a circular pattern.
1. ```spreadAmount```
    - This randomly chooses a slight offset distance between 0.1 and 0.2. This prevents every marker from being in a perfect circle pattern
2. ```angle```
    - This one uses an index of the marker to determine its placement angle on a circle. It spreads markers in a spiral pattern to make sure they all don't shift into the same direction
3. ```return```
    - This makes it so that the original lon/lat is slightly shifted so that the marker will go outward

I wouldn't say I've fully mastered Mapbox, but I'm very much learning more and more!

## Wins

### ReliefWeb API
One of the biggest wins for me was definitely this one. I'm happy that I successfully integrated the ReliefWeb API into my project. I definitely didn't think it'd be easy but I felt like I wanted to broaden my knowledge and do something new on my last project, something that I've never done before.

The proxy now powers both the interactive Mapbox GL JS map and the dashboard statistics that is used for Recharts.

### Marker Overlap Problem with Math
This is one of the wins I'm happy about. As I said before, there are multiple disasters that are placed in the exact same coordinates by ReliefWeb API. Initially, Mapbox would just stack them on top of eachother due to the coordinates being the same so it was impossible to see or click the overlapping markers. 

To solve this, I wrote that ```spreadMarkers``` function to basically do it's name job. It pushes each marker into a different direction outwards so that the user can finally click on them!

### Tab Navigation for Register/Login Flow
One of the wins I'm proud of is building a clean and intuitive tab system for toggling between registeration and login forms. I was going to split them into different pages, similar to my previous projects but then I decided to trying something new and found ```@headlessui/react```'s ```TabGroup``` to create a smooth toggle interface for the user.

I made a small piece of UI that would be very user-friendly to me, it was the fact that I synced the tab state with the URL string by using ```useSearchParams```. This means the user can directly visit a direct tab by visiting ```/authenticate?tab=register``` or ```/authenticate?tab=login``` (even though they wont write that haha, it was just something I wanted to try and do).

## Key Learnings/Takeaways

- I feel even more confident when using React hooks such as useState, useEffect, useSearchParams. I'm not 100% onto it fully but I can get by with it.

- I learned how to integrate an external API that doesn't behave like a typical REST API. Working with ReliefWeb taught me how to send structured POST queries as it's not just a simple GET request for complex filters.

- I have just found out about Mapbox GL JS for the first time so I'm still very beginner on it. I learned how to display dynamic markers and handle zoom, click events and work around edge cases like stacked coordinates though.

- I improves my understanding of authentication flows, especially handling things like JWT storage, protected routes, and syncing form state across tabs.

- I learned how to use ```@headlessui/react``` components such as  ```Tab``` series, ```Dialog``` series, and ```Button``` to build a clean, accessible UI without starting from scratch.

- I built my very first data dashboard by using Recharts which I've not touched before. I used different chart types like Pie, Radar, and Line to visualize the humanitarian disaster trends.

## Bugs

- The marker spreading logic works, but I don't 100% fully understand how the math makes it work. It fixed the issue though so I kept it.

- After deleting an account, the app tries to re-fetch the exact profile one last time, which always triggered a ```401 Unauthorized``` error. I had to add logic to prevent this fetch from running after the account is gone.

## Future Improvements

- Add a theme toggle so users can swap between dark mode and light mode.

- Add something like a spinning globe gif or some animation that will replace the "Loading..." text.

- Add filtering and search options for disasters on the map.

- Now that I've done the marker spread function, technically I can go back into loading markers based on the users view boundary.