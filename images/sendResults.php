<?php
	
	$input = file_get_contents('php://input');
	$posted = json_decode($input, true);

	$user = $posted['user'];
	$tasks = $posted['tasks'];


	try {
		
		$dbh = new PDO('mysql:dbname=Images;host=localhost', 'root', null);
		
		$sth = $dbh->prepare("INSERT INTO Subjects(Name, Mail, Course) VALUES ('".$user['name']."', '".$user['mail']."', ".$user['course'].")");

		$sth->execute();
		$sid = $dbh->lastInsertID();

		foreach ($tasks as $i => $task) {
			$sth = $dbh->prepare("INSERT INTO Tasks(Subject_ID, Type) VALUES (".$sid.", ".$task['type'].")");
			$sth->execute();
			$tid = $dbh->lastInsertID();

			foreach ($task['tests'] as $j => $test) {
			
				$sth = $dbh->prepare("INSERT INTO Tests(Task_ID, Scene, Object, Rate) VALUES (".$tid.", ".$test['scene'].", ".$test['object'].", ".$test['rate'].")");
				$sth->execute();
			}
		}
	
		$dbh = null;
	}
	catch(Exception $e) {
	  
	}
?>