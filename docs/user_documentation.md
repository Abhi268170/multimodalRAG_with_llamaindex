

---

# User Guide: PDF Multimodal Search

This guide explains how to use the PDF Multimodal Search tool. It lets you search inside PDF documents using words or even pictures!

## What is this tool?

Imagine you have a PDF document, like a report with text and charts. This tool helps you find information in that PDF, not just by searching for specific words, but also by searching for things that look like a picture you give it.

It works by:
1.  Reading your PDF, page by page.
2.  Understanding both the text and the images on each page.
3.  Saving this understanding in a special search database.
4.  Allowing you to ask questions (with text or pictures) to find the most similar pages in your PDF.

You can use it either by typing commands in your computer's terminal (Command Line Interface, CLI) or by opening a simple webpage in your browser (Web User Interface, Web UI).

## What you need

Before you start, make sure you have a few things ready:

1.  **The tool's files:** You need to have downloaded or copied the project files onto your computer.
2.  **Python:** You need Python installed (version 3.8 or newer is best).
3.  **The "search helper" running:** This tool uses a special database called Qdrant to help with searching. You need to have Qdrant running on your computer or accessible over a network. The tool is set up by default to look for it at `http://localhost:6333/`. (If you don't know what this is, you might need someone to help you set it up first).
4.  **An extra helper for images (sometimes):** To turn PDF pages into images, the tool uses another program called Poppler. Depending on your computer system, you might need to install this separately if the initial setup doesn't include it.

## Getting Started

1.  **Open your terminal or command prompt:** Navigate to the folder where you put the tool's files.
2.  **Install needed parts:** Run this command to get the necessary Python libraries:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Make sure Qdrant is running:** Start your Qdrant service if it's not already active.

Now you can use either the command line or the web interface.

## Using the Command Line Interface (CLI)

The CLI lets you perform tasks by typing specific commands.

You run commands using `python cli.py` followed by what you want to do.

### 1. Upload and Index a PDF

This command reads a PDF file and adds its content to the search database.

*   **Command:** `upload`
*   **What you need:** The path to the PDF file on your computer.

```bash
python cli.py upload /path/to/your/document.pdf
```

Replace `/path/to/your/document.pdf` with the actual path to the PDF file you want to search.

*   **What happens:** The tool will process the PDF page by page. This might take some time, especially for large PDFs. It will print messages as it works.
*   **Result:** If successful, it will tell you the PDF was indexed and give you a unique ID for that PDF (a long string of letters and numbers).

### 2. Search by Text

This command lets you search the indexed PDFs using a sentence or keywords.

*   **Command:** `search-text`
*   **What you need:** The words you want to search for, in quotes (`"`).
*   **Option:** You can add `--limit` followed by a number to say how many results you want (default is 3).

```bash
python cli.py search-text "what are the main findings?"
```
or
```bash
python cli.py search-text "diagram of the system" --limit 5
```

*   **What happens:** The tool searches the database to find pages where the text content is similar to your query.
*   **Result:** It will print a list of matching pages, showing which PDF and page number it is, a snippet of the text from that page, the image file path (on the server), and a score (how well it matched, higher is better).

### 3. Search by Image

This command lets you search the indexed PDFs using a picture file.

*   **Command:** `search-image`
*   **What you need:** The path to the image file on your computer.
*   **Option:** You can add `--limit` followed by a number to say how many results you want (default is 3).

```bash
python cli.py search-image /path/to/your/query_picture.png
```
or
```bash
python cli.py search-image /path/to/another/image.jpg --limit 5
```

*   **What happens:** The tool looks at your query image and searches the database to find pages where the *image* content is visually similar to your query image.
*   **Result:** It will print a list of matching pages, similar to the text search results (PDF ID, page number, text snippet, image file path, and score).

## Using the Web User Interface (Web UI)

The Web UI provides a simple webpage to interact with the tool using your browser.

### 1. Start the Web App

Open your terminal in the project folder and run:

```bash
python app.py
```

*   **What happens:** The program will start a small web server. It will print a message like `* Running on http://127.0.0.1:5000/`.
*   **Keep this terminal open:** The web app needs this running.

### 2. Open in your Browser

Open your web browser (like Chrome, Firefox, Safari) and go to the address shown in the terminal, usually:

`http://127.0.0.1:5000/`

You should see a page titled "PDF Multimodal Search".

### 3. Upload a PDF

Use the "Upload PDF" section on the left.

1.  Click the "Choose File" button and select a PDF file from your computer.
2.  Click the "Upload and Index" button.

*   **What happens:** The page will show a "Processing PDF..." message. This takes time. Once done, a green "success" message will appear showing the PDF ID and number of pages. If there's a problem, a red "error" message will appear.

### 4. Search the PDF

Use the "Search PDF" section on the right.

*   Choose either **"Text Search"** or **"Image Search"** by clicking the tabs.

*   **For Text Search:**
    1.  Type your question or keywords into the "Search Query" box.
    2.  (Optional) Change the "Result Limit" number.
    3.  Click the "Search" button.

*   **For Image Search:**
    1.  Click "Choose File" under "Select Image File" and select an image from your computer.
    2.  (Optional) Change the "Result Limit" number.
    3.  Click the "Search" button.

*   **What happens:** The page will show a "Searching..." message. Once done, results will appear below the search section. If no results are found, it will say so.

### 5. View Search Results

Search results appear as cards. Each card shows:

*   **PDF ID:** Which PDF the result came from.
*   **Page:** The page number in that PDF.
*   **Score:** A number showing how well this page matched your search (closer to 1 is a better match).
*   **Image:** A small picture of the page. **Click on the image to see it bigger** in a fullscreen view. Press `Esc` or click outside the image to close the fullscreen view.
*   **Text Preview:** A snippet of the text found on that page.

## Important Notes

*   **Qdrant Must Be Running:** The tool cannot work if the Qdrant search helper is not running.
*   **Data Resets:** Every time you stop and restart the web app (`python app.py`) or run a new command with `python cli.py`, the search database is cleared and rebuilt. Your uploaded PDFs are *not* saved permanently in the database index between runs. You have to re-upload PDFs each time you start fresh.
*   **Image Files:** When you upload a PDF, the tool creates image files for each page. These are stored temporarily in the `images` folder in the project directory. For the web app, these images might be cleared when you upload a *new* PDF.
*   **Processing Takes Time:** Uploading and indexing a PDF can take a while, especially for long documents or if your computer is slow.

That's it! You can now start exploring your PDF documents using text and image search.