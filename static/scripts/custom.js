$(document).ready(function(){
    $('.add-to-selection').on("click",function(){

      


       let button = $(this)
       let id = button.attr("data-index")
       let hotel_id = $("#id").val()
       let room_id = $(`.room_id_${id}`).val()
       let room_number = $(`.room_number_${id}`).val()
       let hotel_name = $("#hotel_name").val()
       let room_name = $("#room_name").val()
       let room_price = $("#room_price").val()
       let room_type = $("#room_type").val()
       let number_of_beds = $("#number_of_beds").val()
       let checkin = $("#checkin").val()
       let checkout = $("#checkout").val()
       let adult = $("#adult").val()
       let children = $("#children").val()

       console.log(hotel_id);
       console.log(room_id);
       console.log(room_number);
       console.log(hotel_name);
       console.log(room_name);
       console.log(room_price);
       console.log(number_of_beds);
       console.log(checkin);
       console.log(checkout);
       console.log(adult);
       console.log(children);

       $.ajax({

          url:'/booking/add_to_selection/',
          data:{
            "id": id,
            "hotel_id":hotel_id,
            "room_id":room_id,
            "room_number":room_number,
            "hotel_name":hotel_name,
            "room_type":room_type,
            "room_name":room_name,
            "room_price":room_price,
            "number_of_beds":number_of_beds,
            "checkin":checkin,
            "checkout":checkout,
            "adult":adult,
            "children":children,
          },
          dataType: "json",
          beforeSend:function(){
            console.log("Sending data to server...");
            button.html("<i class='fas fa-spinner fa-spin'></i> Processing")
            
          },
          success:function(response){
            console.log(response);
            $(".room-count").text(response.total_selected_items)
            button.html("<i class='fas fa-check'></i> Added To Selection")

          }
          
       })
    })

})

$(document).on("click",".delete-item",function(){
  let id = $(this).attr("data-item")
  let button=$(this);
  Swal.fire({
    title:"Are you sure want to delete this room?",
    text:"You Won't be able to revert this!",
    icon:"warning",
    showCancelButton: true,
    confirmButtonColor:"#3085d6",
    cancelButtonColor:"#d33",
    confirmButtonText:"Yes,delete it!"

  }).then((result)=>{
    if (result.isConfirmed){
      $.ajax({
        url:"/booking/delete_selection/",
        data:{
          "id":id
        },
        dataType:"json",
        beforeSend:function(){
          button.html("<i class='fas fa-spinner fa-spin'></i>");
        },
        success:function(res){
          console.log(res.total_selected_item);
          $(".room-count").text(res.total_selected_item);
          $(".selection-list").html(res.data);
        },
      });
  
    }

  });
});

function makeAjaxCall(){
  $.ajax({
    url:"/update_room_status/",
    type:"GET",
    success:function(data){
      console.log("Checked Rooms");
    },
   
  });
}
setInterval(makeAjaxCall,86400000);
// setInterval(makeAjaxCall,86400000);



