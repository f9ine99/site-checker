from flask import Flask, render_template, request
import asyncio
import aiohttp
from werkzeug.utils import secure_filename

app = Flask(__name__)

statuses = {
    200: "200 OK Website Available 👍",
    301: "301 Permanent Redirect ⏳",
    302: "302 Temporary Redirect ⏳",
    404: "404 Not Found 😔",
    500: "500 Internal Server Error 😞",
    503: "503 Service Unavailable 😞"
}

async def check_website(session, url):
    try:
        async with session.get(url) as response:
            status = statuses.get(response.status, "Unknown Status ❌")
            return url, status
    except aiohttp.ClientError:
        return url, "Failed to respond"

@app.route('/', methods=['GET', 'POST'])
def index():
    num_websites = 0
    website_urls = []

    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        single_url = request.form.get('single_url')  # Get the single URL input

        if uploaded_file:
            if uploaded_file.filename.lower().endswith('.txt'):
                filename = secure_filename(uploaded_file.filename)
                lines = uploaded_file.read().decode("utf-8").splitlines()
                num_websites = len(lines)
                website_urls.extend(lines)
            else:
                return render_template('error.html', error_message='Invalid file format. Please upload a text file.')
        elif single_url:  # Check if a single URL was submitted
            num_websites = 1
            website_urls.append(single_url)
        else:
            num_websites = int(request.form['num_websites'])
            for i in range(num_websites):
                url = request.form.get(f"url_{i+1}")
                website_urls.append(url)

        async def main():
            async with aiohttp.ClientSession() as session:
                tasks = [check_website(session, url) for url in website_urls]
                results = await asyncio.gather(*tasks)

            return render_template('results.html', results=results)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(main())

    return render_template('index.html', num_websites=num_websites)

if __name__ == '__main__':
    app.run(debug=True)