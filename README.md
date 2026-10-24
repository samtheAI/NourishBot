# NourishBot

NourishBot is a Streamlit food-vision app powered by Groq. Upload a fridge or ingredient photo to create a tailored recipe, or upload a finished dish to estimate calories, protein, carbohydrates, fat, fiber, sugar, and sodium.

## Features

- Two workflows: recipe generation and nutrition analysis
- Dietary preference and restriction input
- Image compression before the Groq request
- Structured nutrition and recipe output
- Four one-click examples
- Responsive dark interface inspired by the supplied reference screenshots
- Friendly empty, loading, configuration, and error states

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY="your-key"
streamlit run app.py
```

The app uses `qwen/qwen3.8-27b` by default. Override it with `GROQ_MODEL` if needed.

## Deploy on Streamlit Community Cloud

1. Create an app from this repository and set the entry point to `app.py`.
2. Open **Advanced settings → Secrets**.
3. Add:

   ```toml
   GROQ_API_KEY = "your-key"
   ```

4. Deploy.

Nutrition values are inferred from an image and are estimates, not medical advice.

## Example image credits

Example photographs are served from files committed to this repository and sourced from Unsplash:

- [Steak pasta](https://unsplash.com/photos/1551183053-bf91a1d81141)
- [Vegetable bowl](https://unsplash.com/photos/1547592180-85f173990554)
- [Fresh market bowl](https://unsplash.com/photos/1490645935967-10de6ba17061)
- [Chicken pizza](https://unsplash.com/photos/1565299624946-b28f40a0ae38)

