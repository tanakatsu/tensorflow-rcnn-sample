# R-CNN sample on Heroku

This is a example of R-CNN that is working on Heroku.

- Image Recognition
	- [TensorFlow](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/models/image/imagenet/classify_image.py)
- Object segmentation
	- [Selective Search](https://github.com/AlpacaDB/selectivesearch) by Alpaca

### How to deploy to Heroku

1. Install the container-registry plugin (if you have not installed yet)

	```
	$ heroku plugins:install heroku-container-registry
	```

1. Create a Heroku application

	```
	$ heroku create [your_app_name]
	```

1. Build the image and push to the Heroku container registry

	```
	$ heroku container:push web
	```

1. Open the app in your browser

	```
	$ heroku open
	```

### Running local

```
$ pip install -r requirements.txt
$ pip install numpy 
$ pip install scipy
$ pip install scikit-image
$ pip install selectivesearch
$ python main.py
```
Then, open your browser and navigate to http://localhost:5000

### Demo

- [https://tanakatsuyo-tf-rcnn-test.herokuapp.com/](https://tanakatsuyo-tf-rcnn-test.herokuapp.com/)

	Note: no consideration for simultaneous access