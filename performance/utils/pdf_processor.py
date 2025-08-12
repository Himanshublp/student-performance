import PyPDF2
import re
import pandas as pd
def extract_data_from_pdf(pdf_file):
    """
    Extract data from a PDF file.
    :param pdf_file: A file-like object (InMemoryUploadedFile from Django)
    :return: A structured list of dictionaries containing semester-wise data.
    """
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    content = ''.join(page.extract_text() for page in pdf_reader.pages)

    semesters = []
    semester_pattern = re.compile(r"Semester : (\d+) Even/Odd : (Even|Odd).*?SGPA : ([\d.]+)", re.S)
    subject_pattern = re.compile(
        r"(?P<code>\w+)\s+(?P<name>.+?)\s+(Theory|Practical|CA)\s+(?P<internal>\d+)\s+(?P<external>\d+|--)\s+(?P<grade>\w+)"
    )

    # Extract semester-level details
    for semester_match in semester_pattern.finditer(content):
        semester_number = int(semester_match.group(1))
        semester_sgpa = float(semester_match.group(3))

        # Extract subjects under this semester
        semester_block = semester_match.group(0)
        subjects = []
        for subject_match in subject_pattern.finditer(semester_block):
            subjects.append({
                "code": subject_match.group("code"),
                "name": subject_match.group("name"),
                "internal": int(subject_match.group("internal")),
                "external": subject_match.group("external"),
                "grade": subject_match.group("grade"),
            })

        semesters.append({
            "semester_number": semester_number,
            "sgpa": semester_sgpa,
            "subjects": subjects,
        })

    return semesters
def save_data_to_csv(data, output_file='results.csv'):
    """
    Save the extracted data to a CSV file.
    :param data: List of dictionaries containing extracted data.
    :param output_file: The name of the output CSV file.
    """
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)