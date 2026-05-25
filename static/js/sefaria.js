// Sefaria 주석 팝업 처리

$(document).on('click', '.sefaria_btn', function () {
    var ref = $(this).data('ref');

    // 제목: "Genesis.1.1" → "Genesis 1:1"
    var parts = ref.split('.');
    var bookDisplay = parts[0].replace(/_/g, ' ');
    var title = bookDisplay + ' ' + parts[1] + ':' + parts[2];

    $('#sefariaModalLabel').text('Sefaria 주석 — ' + title);
    $('#sefariaModalBody').html(
        '<div class="text-center py-4"><span class="text-muted">불러오는 중...</span></div>'
    );
    $('#sefariaModal').modal('show');

    $.get('/bhsheb/sefaria/' + ref + '/')
        .done(function (data) {
            var jpsText = data.jps || '';
            var links   = Array.isArray(data.links) ? data.links : [];

            var html = '';

            // ── JPS 번역 (맨 위) ──────────────────────────────────────────
            if (jpsText) {
                html += '<div class="mb-3 pb-2 border-bottom">';
                html += '<p class="mb-1"><strong>📘 JPS TANAKH (영문 번역)</strong></p>';
                html += '<p class="small" style="color:#333;">' + jpsText + '</p>';
                html += '</div>';
            }

            // ── 주석/타르굼/미드라쉬 ──────────────────────────────────────
            if (links.length === 0 && !jpsText) {
                $('#sefariaModalBody').html(
                    '<p class="text-muted">해당 구절의 주석이 없습니다.</p>'
                );
                return;
            }

            if (links.length > 0) {
                // 카테고리 순서 정렬
                var ORDER = ['Commentary', 'Targum', 'Midrash'];
                links.sort(function (a, b) {
                    return ORDER.indexOf(a.category) - ORDER.indexOf(b.category);
                });

                var currentCat = '';
                $.each(links, function (i, item) {
                    if (item.category !== currentCat) {
                        currentCat = item.category;
                        var catLabel = {
                            'Commentary': '📖 주석 (Commentary)',
                            'Targum':     '📜 타르굼 (Targum)',
                            'Midrash':    '📚 미드라쉬 (Midrash)'
                        }[currentCat] || currentCat;
                        html += '<h6 class="mt-3 mb-2 text-secondary border-bottom pb-1">' + catLabel + '</h6>';
                    }

                    html += '<div class="sefaria-item mb-3">';
                    html += '<p class="mb-1"><strong>' + item.source + '</strong>';
                    html += ' <small class="text-muted">' + item.ref + '</small></p>';
                    if (item.text) {
                        html += '<p class="sefaria-text small">' + item.text + '</p>';
                    } else {
                        html += '<p class="text-muted small">영문 번역 없음</p>';
                    }
                    html += '</div>';
                });
            }

            $('#sefariaModalBody').html(html);
        })
        .fail(function () {
            $('#sefariaModalBody').html(
                '<p class="text-danger">주석을 불러오는 데 실패했습니다. 잠시 후 다시 시도해 주세요.</p>'
            );
        });
});
