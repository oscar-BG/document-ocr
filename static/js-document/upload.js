$(document).ready(function() {

    // Funcion que se ejecuta cuando se enviá los documentos a procesar
    $("#form_document").on("submit", function(event) {
        event.preventDefault();

        Swal.fire({
            title               : "Procesando documento",
            timerProgressBar    : true,
            allowOutsideClick   : false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        $.ajax({
            url         : $(this).attr("action"),
            type        : "POST",
            data        : new FormData(this),
            processData : false,
            contentType : false,
            success: function(response) {
                Swal.close();
                if (response.success) {
                    location.reload();
                }
            }
        });

    });
});