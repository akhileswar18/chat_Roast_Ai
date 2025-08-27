# Chat Roast

`Chat Roast` is a playful chat analyser that turns your exported WhatsApp chats into a collection of colourful charts and tongue‑in‑cheek observations.  
Drop in a text transcript exported from WhatsApp and it will:

* Parse every message and attribute it to the sender.
* Count how many messages each participant sent and show you who dominated the conversation.
* Plot activity over time (by day and by hour) to expose late night chatting and sleepy Mondays.
* List your most common words and emojis so you can finally admit you overuse 😂.
* Generate a short “roast” of your chat with a light‑hearted tone.

This is a lightweight proof of concept based on the “Chat Roast” product described in the provided PDF.  It runs entirely locally and does not upload or store your data anywhere.

## Quick start

1. **(Optional)** Install the Python dependencies.  This script depends only on `matplotlib` for plotting, which is already available in most Python environments.  If your Python does not include it you can install it with:

    ```bash
    pip install matplotlib
    ```

2. Export a WhatsApp chat from your phone (without media) and save the `.txt` file in the project directory.  You can also use the provided `sample_chat.txt` for testing.

3. Run the analyser:

    ```bash
    python main.py --input sample_chat.txt --output output
    ```

4. The script will produce a few PNG images in the `output/` directory and print a playful roast to the console.

## Project structure

```
chat_roast/
│   main.py               # command line entry point
│   whatsapp_parser.py    # parser for exported WhatsApp chats
│   analysis_utils.py     # helper functions to compute statistics
│   roast_engine.py       # generates witty roast comments
│   requirements.txt      # list of third‑party dependencies
│   sample_chat.txt       # small sample transcript for demonstration
└── README.md             # this file
```

## Limitations

This proof of concept supports the most common English export format of WhatsApp (e.g. `MM/DD/YY, HH:MM AM/PM - Name: Message`).  Other locales or formats may require additional parsing logic.  The “roast” engine uses simple templates rather than a machine learning model, so feel free to extend it with your own humour.