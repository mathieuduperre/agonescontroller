function gscreate() {
    var name = $("#name").val();
    var brand = $("#image").val();
    data = {'name': name, 'image': image};
    $.ajax({
         type: "POST",
          url: '/gsradd',
          dataType: 'json',
          data: data,
          success: function(data) {
               if (data.result == 'success') {
                $("body").overhang({message: "Gameserver "+name+" Created!!!", type: "success"});
               } else {
                $("body").overhang({message: "Gameserver "+name+" Failed to Create Because "+data.reason, type: "error", closeConfirm: true});
               };
          }
    });
}

function gsdelete(name) {
    data = {'name': name};
    $.ajax({
         type: "POST",
          url: '/gsdelete',
          data: data,
          dataType: 'json',
          success: function(data) {
              if (data.result == 'success') {
                $("body").overhang({message: "Gameserver "+name+" Deleted!!!", type: "success"});
                gslist();
              } else {
                $("body").overhang({message: "Gameserver "+name+" Failed to Delete Because "+data.reason, type: "error", closeConfirm: true});
              };
          }
    });
}

function gslist() {
    $.ajax({
         type: "GET",
          url: '/gslist',
          //dataType: 'json',
          success: function(data) {
          $('#gs').html(data);
          }
    });
}
