# Model files go here

Place your trained artifacts in this folder with these exact filenames:

- `lstm_model.h5` — the trained Keras model
- `tokenizer.pkl` — the fitted `Tokenizer` object (pickled)
- `max_len.pkl` — the integer max sequence length used during training (pickled)

These are the same three files your original Streamlit app loaded, so if you
already have them from training, just copy them in — no retraining needed.

**Why they're not in this repo:** large binary model files bloat Git repos
and often exceed upload/hosting limits. For version control, use
[Git LFS](https://git-lfs.com/) or host the model on Hugging Face Hub / S3
and download it in your deployment's startup script instead of committing it.
