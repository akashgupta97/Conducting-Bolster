# Conducting-Bolster

In the first phase a simple circuit was created to test the feasibility of the idea proposed. We wanted to create vibrations. So 2 things that came to our minds that are able to 	convert electrical signals to vibrations were motors and piezo transducers. We tried making a circuit with piezo transducers. A basic bone conduction circuit was ready. But the volume of the sound emitted from the vibrations of the transducers was very less. A person needed to be in a silent place to listen this.
In phase two, we tried increasing the volume by increasing the complexity of the circuit. So, we attached an amplifier in between to amplify the signal. For that, we used a PAM8403 class D amplifier. After adding this amplifier, the quality of sound got better. Volume was high enough with this amplifier, that we were able to hear from a distance through our outer ear also. A voltage regulator was also attached to limit the power supply.
In phase three, we attached the whole circuit to a cardboard panel so as to fit inside the pillow to create the final model. We also created an android application that contained basic alarm system. Also a bluetooth module and accelerometer was attached to the circuit so as to communicate with the smartphone and efficient transfer of data.
In Final testing the pillow was tested to by all members of the group and others and feedback was collected.

### Data - 

The circuit is attached with an accelerometer. Accelerometer is used to transfer data from the circuit to the smartphone. The android application displays the values of the sent by the accelerometer. The accelerometer is attached with the Bluetooth module so that there is efficient communication between the pillow and smartphone. The data sent corresponds to the co-ordinate values (x, y, z) in 3-D space which tells us the orientation of the accelerometer. The accelerometer tells based on the activity of the person, whether the person is in deep sleep phase or not. Based on the data, the app responds whether to wake up the person or not. 

### Performance parameters - 

Parameters are used to check the performance of our system. The performance of the model should be highly accurate since any error can lead to malfunction. The performance parameters include:-
1)	Sleep index :- Reports how much the person is satisfied with his sleep or the efficiency. 
2)	Duration:- Reports how long the person sleeps and the duration of his deep sleep phase
3)	Health index: - Reports how much healthy a person feels when he wakes up.
These parameters were measured for a couple of months and a satisfactory improvement was reported by the person.
