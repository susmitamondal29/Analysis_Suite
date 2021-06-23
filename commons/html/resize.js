var w = $(window).width()

function setupHeader() {
    $.getJSON(window.location.href+"/extraInfo.json")
        .done(function(data) {
            $('#page-title').html(data["Title"]);
            data["Subdirectory"].forEach(function(item, index) {
                if (index == 0) {
                    $("<h2>", {
                        html: "Plots by Channel:<br>"
                    }).appendTo($("#channels"));
                }
                $("<a>", {
                    href: "./" + item,
                    html: item
                }).appendTo("#channels");
                $("#channels").append((index+1 < data["Subdirectory"].length) ? " - " : "");
            })
        });
}

function setupImages() {
    console.log(w)
    minSize = 500;
    el_per_line = (Math.floor(w/minSize) == 0) ? 1 : Math.floor(w/minSize);
    el_in_row = 0;

    $("#picTable").html("");
    $.ajax({
        url: window.location.href + "/plots/.",
        success: function(data) {
            row = $("<tr>").appendTo($("#picTable"));
            $(data).find('a[href*=".png"]').each(function() {
                if (el_in_row+1 >  el_per_line) {
                    row = $("<tr>").appendTo($("#picTable"));
                }

                plot = this.innerHTML.replace(".png", "")
                element = $("<td>").appendTo(row)
                $("<img>", {
                    src: "./plots/" + this.innerHTML,
                    class: "autoResizeImage"
                }).appendTo(element);
                element.append("<br>")
                $("<a>", {
                    href: "./logs/" + plot + "_info.log",
                    html: "[log]"
                }).appendTo(element)
                element.append(" - ")
                $("<a>", {
                    href: "./plots/" + plot + ".pdf",
                    html: "[pdf]"
                }).appendTo(element)
                el_in_row += 1
            })
        }
    });
}



function resizeImages() {
    var newWidth = $(window).width()
    console.log(w, newWidth)
    if (w != newWidth) {
        w = newWidth;
        setupImages();
    } else {
        return;
    }
}
