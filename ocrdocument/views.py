from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.files import File
from .forms import SubirDumentoImagenForm
from .models import SaveFileCsv
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from dotenv import load_dotenv
import os
import csv
import locale


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'media/credencials/ocr-document.json'
load_dotenv()
locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')


endpoint        = os.getenv('ENDPOINT')
location        = os.getenv('LOCATION') 
project_id      = os.getenv('PROJECT_ID')
processor_id    = os.getenv('PROCESSOR_ID')

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
            get_text_form_pdf_ocr(url_format)

        return JsonResponse({"success" : True})


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
        

        print(f"There are {len(document.pages)} page(s) in this document.")
        # Convertir el objeto document a un diccionario
        # serialized_document = documentai.Document.to_dict(document)
        # Guardar el diccionario como JSON
        # with open("media/document.json", "w") as json_file:
            # json.dump(serialized_document, json_file, indent=4)
        
        # data = [[entity.mention_text for entity in document.entities if entity.type_ == 'CARD_ID'],
        #   [entity.mention_text for entity in document.entities if entity.type_ == 'FULL_NAME']]

        
        array_card_id = []
        array_full_name = []
        for entity in document.entities:
            card_id = ""
            full_name = ""

            if entity.type_ == 'CARD_ID':
                card_id = int(entity.mention_text)
                array_card_id.append(card_id)
            elif entity.type_ == 'FULL_NAME':
                full_name = entity.mention_text
                array_full_name.append(full_name.replace("\n", " "))

        
        print(array_card_id)
        print(full_name)

        array_card_id_sorted = sorted(array_card_id)
        array_full_name_sorted = sorted(array_full_name, key=locale.strxfrm)
        
        csv_file_name = os.path.splitext(os.path.basename(file_path))[0] + ".csv"
        csv_file_path = os.path.join("media/csv/", csv_file_name)
        relative_csv_file_path = os.path.relpath(csv_file_path, settings.MEDIA_ROOT)


        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['CARD_ID', 'FULL_NAME'])  # Escribir encabezados
            for card_id, full_name in zip(array_card_id_sorted, array_full_name_sorted):
                writer.writerow([card_id, full_name])

        new_csv_instance = SaveFileCsv.objects.create(excel_file=relative_csv_file_path, name_document=csv_file_name)
        
        return True
    except Exception as e:
        print(e)
        return None
    
