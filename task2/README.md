## Question 1.
- Can multiple instances of Trainer be run in parallel to be fault tolerant?
- How different can be result models of Trainer if they are run on the same set
of images? Can they be interchanged?
- How often can we expect any of the service to fail?
- There should be services that receive images from mobile phones and send them back?
How do they work? CPU, RAM, time per image, can be parallel?
- How do Classifier reloads models? How long does it take?
- Are there any mechanisms in Classifier that it can be notofied about new model?
- 

## Question 2.

### Thoughts
- Doing some simple math, it can be seen, that 1 instance of Classifier
can process 5 images in 200ms (time for 1 instance of Preclassifier per image) and
25 images per second. This means to deal with 200 images/sec we would need to have
8 instances of Classifier and 5 instances of Preclassifier per each, 40 in total.
These assumptions are made with no consideration of disk or network latencies and
time that is needed to load new snake model. So generally we would need 20% more
instances, let's say.
- To solve the issue of which image goes where we can use some queueing mechanism.
- It is definitly reasonable to run Trainer in background/parallel
to working Classifier and Preclassifier. As we still have disk/network latencies, 
Trainer should start generating new model as soon as it has finished the previous one.

### Application architecture

- Mobile application: sends a picture ->
- Backend API: it should receive a picture and put info about it in queue for next free
Preclassifier to pick it up for processing ->
- Queue: stores data about yet unprocessed images ->
- Preclassifier (many of them): picks next available unprocessed image from queue and processes it,
and puts the the next queue for Classifier ->
- Queue: stores data about processed by Preclassifier images for Classifier ->
- Classifier (many of them): pick up next available image, processed it returns output to API and
stores info for Trainer's next model generation ->
- Backend API: sends back result to mobile application -> 
- Mobile application: receives back info about the picture and displays it

- Trainer should run constantly regenerating models, as soon as it finishes it or some other 
small service should create an event of model reload in Classifiers (and Preclassifiers)

### Infrastructure

As we have make similar components, let's assume that we would run everything in Kubernetes.
We would need to set up the following:
- Application load balancer: balances traffic from mobile app to Backend API. Usually, this
service is cloud-managed, so we don't need to worry about it. Traffic can come directly from
ALB to ingress of Kubernetes cluster. (Also additionally we would like to obtain a persisting
IP and DNS name for our ALB, Elastic IP and Route53 can help)
- Through ALB and Ingress traffic should get to Backend API. We should have several instances
 of it for fault tolerance (ideally, at least 1 instance per worker node). Backend API should
 save image to a shared storage that can be accessed later by Preclassifier, Classifier and 
 Trainer (we can use EFS or S3). Also Backend API should put info about new received image to
 queue (we can use self-hosted Kafka or AWS managed MSK).
- Then 5 instances of Preclassifier (per 1 instance of Classifier) should process the image
and put info about them into next queue for Classifier and JSON output to shared storage.
- Classifier processes images, write output to to the queue for Backend API to respond back
to mobile application.
- Trainer is constantly regenerating new models based on images found in specific location,
determined by where Classifier puts the image.
- Maybe reload of Classifier's model can be triggered with some serverless function as Lambda.


Summing up, we would need:
- Application load balancer with persistent IP and DNS name (ALB, Elastic IP, Route53)
- EKS with about 4 nodes. It would be good to have half RAM and CPU kept free for server
faults, so load can be quickly moved to healthy nodes. Each node would have 2 Classifiers,
 10 Preclassifiers and Backend APi running. Also there will be additional services, like
Kafka, Trainers and other be runnning, and there is an overhead coming from Kubernetes. 
If assuming having 4 nodes, they should have at least 32GB RAM and 48 vCPU (or we can go 
with more smaller instances). As these services
are compute intensive, I would consider Compute Optimized instances in AWS. 
- Depending on whether selfhosting Kafka is desired, we could use either Kafka itself or AWS MSK.
- A shared storage is needed to be accessible by all components of application. S3 of EFS.

### Server Faults

- Backend API in this approach is stateless
- Queue should have replication mechanisms
- Multiple Trainers across several machines will allow to overcome its failures
- Kubernetes as an orchestration system would help to redistribute load in case of server fault
- We can also set up horizontal autoscaling in cloud and in Kubernetes to deal with the unexpected 
load. 

### Some other tools
- We would need a lot of CI/CD pipelines (Jenkins, Gitlab CI, Github Actions)
- We wish to have some overview of how the system behaves (meaning we need to have logging
and monitoring)
- Terraform/Cloudformation will help to unify and simply the process of cloud infra setup

I guess, that is what I had in mind, but I'm afraid I missed some things :)


## Bonus 1.


## Bonus 2.

I think that suggested architecture without scaling can deal with peaks of load due to
usage of queues.