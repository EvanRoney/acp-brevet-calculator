<html>
    <head>
        <title>All Brevet Control Times</title>
    </head>

    <body>
        <h1>List of All Times</h1>
        <ul>
            <?php
            $json = file_get_contents('http://web:5000/listAll');
	    $obj = json_decode($json);
	    foreach ($obj as $time) {
		    echo "<li>Open: ".$time->open_time .", Close: ".$time->close_time. "</li>";
	    }
	    $json = file_get_contents('http://web:5000/listOpenOnly');
	    $obj = json_decode($json);
	    foreach ($obj as $time){
	        echo "<li>Open: ".$time->open_time ."</li>";
	    }
	    $json = file_get_contents('http://web:5000/listCloseOnly');
	    $obj = json_decode($json);
	    foreach ($obj as $time){
	        echo "<li>Close: ".$time->close_time ."</li>";
	    }
            ?>
	</ul>
        
    </body>
</html>
