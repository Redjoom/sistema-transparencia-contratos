def save_public_version(doc, output_path):
    doc.save(output_path, garbage=4, deflate=True, clean=True)
