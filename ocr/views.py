
# import io
# import fitz  # PyMuPDF
# from rest_framework.views import APIView
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.response import Response
# from rest_framework import status
# import ocrmypdf
# from django.http import HttpResponse

# class OCRView(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request, *args, **kwargs):
#         file = request.data.get('file')
#         start_match = request.data.get('start_match')
#         end_match = request.data.get('end_match')

#         if not file:
#             return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
#         if not start_match or not end_match:
#             return Response({"error": "Start and end matches must be provided"}, status=status.HTTP_400_BAD_REQUEST)

#         # Create in-memory file for OCR processing
#         input_bytes = io.BytesIO()
#         for chunk in file.chunks():
#             input_bytes.write(chunk)
#         input_bytes.seek(0)

#         # Create in-memory file for OCR output
#         output_bytes = io.BytesIO()

#         try:
#             # Perform OCR on the in-memory file
#             ocrmypdf.ocr(input_bytes, output_bytes, deskew=True, force_ocr=True)
#             output_bytes.seek(0)

#             # Open the OCRed PDF from in-memory bytes
#             doc = fitz.open(stream=output_bytes, filetype="pdf")
#             start_page = None
#             end_page = None

#             # Search for start_match and end_match in the PDF
#             for page_num in range(doc.page_count):
#                 page = doc.load_page(page_num)
#                 text = page.get_text("text")
#                 if start_match in text and start_page is None:
#                     start_page = page_num
#                 if end_match in text:
#                     end_page = page_num
#                     break

#             if start_page is None or end_page is None or start_page > end_page:
#                 return Response({"error": "Start and end matches not found or invalid"}, status=status.HTTP_400_BAD_REQUEST)

#             # Extract the pages between start_page and end_page
#             new_doc = fitz.open()
#             for page_num in range(start_page, end_page + 1):
#                 new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

#             # Save the extracted pages to an in-memory bytes buffer
#             extracted_bytes = io.BytesIO()
#             new_doc.save(extracted_bytes)
#             new_doc.close()
#             doc.close()
#             extracted_bytes.seek(0)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         # Set the Content-Disposition header to force a download with a .pdf extension
#         response = HttpResponse(extracted_bytes.getvalue(), content_type='application/octet-stream')
#         response['Content-Disposition'] = 'attachment; filename="extracted_document.pdf"'
#         return response




import io
import fitz  # PyMuPDF
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import ocrmypdf
from django.http import HttpResponse, JsonResponse
from PIL import Image


class OCRView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "Request successful"}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        file = request.data.get('file')
        start_match = request.data.get('start_match')
        end_match = request.data.get('end_match')

        if not file:
            return JsonResponse({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Create in-memory file for OCR processing
        input_bytes = io.BytesIO()
        for chunk in file.chunks():
            input_bytes.write(chunk)
        input_bytes.seek(0)

        try:
            # Determine if the file is an image or a PDF
            file_type = file.content_type
            if "image" in file_type:
                # Convert image to PDF
                image = Image.open(input_bytes)
                pdf_bytes = io.BytesIO()
                image.save(pdf_bytes, format="PDF")
                pdf_bytes.seek(0)
                input_bytes = pdf_bytes
            elif "pdf" not in file_type:
                return Response({"error": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)

            # Create in-memory file for OCR output
            output_bytes = io.BytesIO()

            # Perform OCR on the in-memory file
            ocrmypdf.ocr(input_bytes, output_bytes, deskew=True, force_ocr=True)
            output_bytes.seek(0)

            # If start_match and end_match are not provided, return a success message
            if not start_match or not end_match:
                return Response({"success": True, "message": "OCR process completed successfully"}, status=status.HTTP_200_OK)

            # Open the OCRed PDF from in-memory bytes
            doc = fitz.open(stream=output_bytes, filetype="pdf")
            start_page = None
            end_page = None

            # Search for start_match and end_match in the PDF
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                if start_match in text and start_page is None:
                    start_page = page_num
                if end_match in text:
                    end_page = page_num
                    break

            if start_page is None or end_page is None or start_page > end_page:
                return Response({"error": "Start and end matches not found or invalid"}, status=status.HTTP_400_BAD_REQUEST)

            # Extract the pages between start_page and end_page
            new_doc = fitz.open()
            for page_num in range(start_page, end_page + 1):
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

            # Save the extracted pages to an in-memory bytes buffer
            extracted_bytes = io.BytesIO()
            new_doc.save(extracted_bytes)
            new_doc.close()
            doc.close()
            extracted_bytes.seek(0)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the byte code of the extracted document
        return HttpResponse(extracted_bytes.getvalue(), content_type='application/octet-stream')
