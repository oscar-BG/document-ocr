from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.core.files import File
from .forms import SubirDumentoImagenForm
from .models import SaveFileCsv
import os
import csv
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'media/credencials/ocr-document.json'
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from dotenv import load_dotenv

load_dotenv()


endpoint = os.getenv('ENDPOINT')
location = os.getenv('LOCATION') 
project_id = os.getenv('PROJECT_ID')
processor_id = os.getenv('PROCESSOR_ID')

# Create your views here.

def formDocument(request):
    return render(request, 'index.html')

def homepage(request):
    form = SubirDumentoImagenForm()
    return render(request, 'index.html', {'form': form})


def upload(request):
    if request.method == "POST":
        form = SubirDumentoImagenForm(request.POST, request.FILES)
        if form.is_valid():
            instancia = form.save(commit=False)
            instancia.save()
            url_document = instancia.documento.url
            url_format = url_document[1:]
            print(url_format)

            get_text_form_pdf_ocr(url_format)
        return redirect("homepage")


def listarData(request):
    # return render(request, 'show_csv.html')

    data = SaveFileCsv.objects.all()
    print(data)
    return render(request=request, template_name="show_csv.html", context={'data' : data})
    
def get_text_form_pdf_ocr(file_path):
    try:
        mime_type = 'application/pdf'
        client = documentai.DocumentProcessorServiceClient(client_options=ClientOptions(api_endpoint=f"{location}-{endpoint}"))

        name = client.processor_path(project_id, location, processor_id)
        with open(file_path, "rb") as image:
            image_content = image.read()

        raw_document = documentai.RawDocument(
            content=image_content, mime_type=mime_type)
        
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        response = client.process_document(request=request)

        document = response.document
        data = []

        
        for entity in document.entities:
            card_id = ""
            last_name = ""
            second_last_name = ""
            name = ""

            if entity.type_ == 'CARD_ID':
                card_id = entity.mention_text
            elif entity.type_ == 'LAST_NAME':
                last_name = entity.mention_text
            elif entity.type_ == 'SECOND_LAST_NAME':
                second_last_name = entity.mention_text
            elif entity.type_ == 'NAME':
                name = entity.mention_text
            
            data.append([card_id.strip(), last_name.strip(), second_last_name.strip(), name.strip()])

        

        csv_data = []
        for row in data:
            csv_data.append([row[0], row[1], row[2], row[3]])
        
        csv_file_name = os.path.splitext(os.path.basename(file_path))[0] + ".csv"
        csv_file_path = os.path.join("media/csv/", csv_file_name)

        relative_csv_file_path = os.path.relpath(csv_file_path, settings.MEDIA_ROOT)

        # filtered_data = [row for row in csv_data if any(cell.strip() for cell in row)]

        # print(filtered_data)

        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['CARD_ID', 'LAST_NAME', 'SECOND_LAST_NAME', 'NAME'])  # Escribir encabezados
            writer.writerows(csv_data)  # Escribir los datos recolectados

        new_csv_instance = SaveFileCsv.objects.create(excel_file=relative_csv_file_path, name_document=csv_file_name)

        return True
    except Exception as e:
        print(e)
        return None
