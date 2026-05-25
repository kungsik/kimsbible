// 평행구 팝업 처리

$(document).on('click', '.parallel_btn', function () {
    var ref = $(this).data('ref');  // 예: "GEN 1:27"

    $('#parallelModalLabel').text('평행구');
    $('#parallelModalBody').html(
        '<div class="text-center py-4"><span class="text-muted">불러오는 중...</span></div>'
    );
    $('#parallelModal').modal('show');

    $.get('/bhsheb/parallel/' + encodeURIComponent(ref) + '/')
        .done(function (data) {
            if (!Array.isArray(data) || data.length === 0) {
                $('#parallelModalBody').html(
                    '<p class="text-muted">평행구가 없습니다.</p>'
                );
                return;
            }

            var html = '';
            var currentType = '';

            $.each(data, function (i, item) {
                if (item.type !== currentType) {
                    currentType = item.type;
                    var typeLabel = item.type === 'HEB' ? '구약' : '신약';
                    html += '<h6 class="mt-3 mb-2 text-secondary border-bottom pb-1">' + typeLabel + '</h6>';
                }

                var displayRef = item.kor_ref || item.ref;
                html += '<div class="parallel-item mb-2">';
                if (item.url) {
                    html += '<a href="' + item.url + '" class="parallel-ref-link">';
                    html += '<strong>' + displayRef + '</strong>';
                    html += '</a>';
                } else {
                    html += '<strong>' + displayRef + '</strong>';
                }
                if (item.text) {
                    html += '<br><small style="color:#333;">' + item.text + '</small>';
                }
                html += '</div>';
            });

            $('#parallelModalBody').html(html);
        })
        .fail(function () {
            $('#parallelModalBody').html(
                '<p class="text-danger">평행구를 불러오는 데 실패했습니다.</p>'
            );
        });
});
