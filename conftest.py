import warnings
# Automatically suppress scikit-image low-contrast warnings in test suite
warnings.filterwarnings("ignore", category=UserWarning, message=".*is a low contrast image.*")
