$(document).ready(function() {
    console.log("DOM carregado.");
    $(document).on('click', '.adiciona-sacola', function() {
        console.log("Botão clicado!");
        const produtoId = $(this).data('produto-id');  // Obtém o ID do produto
        console.log("ID do produto:", produtoId);
        const url = urlAddSacola;  // URL da view
    
        $.ajax({
            type: "POST",
            url: url,
            data: {
                'produto_id': produtoId,
                'csrfmiddlewaretoken': $("meta[name='csrf-token']").attr("content")  // Token CSRF
            },
            success: function(response) {
                alert(response.mensagem);  // Mostra uma mensagem de sucesso
                // Atualiza o subtotal e total no template (se necessário)
                $('#subtotal').text(`Subtotal: R$ ${response.subtotal.toFixed(2)}`);
                $('#total').text(`Total: R$ ${response.total.toFixed(2)}`);
            },
            error: function(error) {
                alert('Erro ao adicionar o produto à sacola.');
            }
        });
    });
});

