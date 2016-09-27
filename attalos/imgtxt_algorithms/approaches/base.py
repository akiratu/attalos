import tensorflow as tf

class AttalosModel(object):
    """
    This class defines an interface that other classes can implement in order to be easily plugged into the driver for the scriptified version of Attalos.

    Required functions to implement:
        __init__
        prep_fit
        prep_predict
        get_training_loss

    Optional
        post_predict
    """

    def __init__(self):
        """
        Initializes object representing Attalos model.
        """
        self.saver = tf.train.Saver()
    
    def initialize_model(self, sess):
        """
        Function responsible for initializing a Tensorflow session.
        Args:
            sess: a Tensorflow session

        Returns:
            nothing
        """
        sess.run(tf.initialize_all_variables())
        
    def save(self, sess, model_output_path):
        """
        Function responsible for saving a Tensorflow session.

        Args:
            sess: a Tensorflow session
            model_output_path: path to write model

        Returns:
            nothing
        """
        self.saver.save(sess, model_output_path)

    def load(self, sess, model_input_path):
        """
        Function responsible for restoring a Tensorflow session.

        Args:
            sess: a Tensorflow session
            model_input_path: path to read model from

        Returns:
            nothing
        """
        self.saver.restore(sess, model_input_path)
        
    def iter_batches(self, dataset, batch_size):
        """
        Function responsible for iterating over a series of batches, given an Attalos dataset and the desired batch_size.
        There should be size(dataset) / batch_size batches.

        Note: this function should be implemented as a generator (yield, not return).

        Args:
            dataset: an Attalos dataset
            batch_size: desired batch size

        Returns:
            yields arguments to be passed to fit()
        """
        # TODO batch_size = -1 should yield the entire dataset
        num_batches = int(dataset.num_images / batch_size)
        for cur_batch_num in xrange(num_batches):
            data = dataset.get_next_batch(batch_size)
            fetches, feed_dict = self.prep_fit(data)
            yield fetches, feed_dict

    def _run(self, sess, fetches, feed_dict):
        vals = sess.run(fetches, feed_dict=feed_dict)
        return vals

    def fit(self, sess, fetches, feed_dict):
        """
        Function responsible for fitting a Tensorflow session model (sess) given fetches and feed_dict.

        Args:
            sess: a Tensorflow session
            fetches: information to be retrieved from the Tensorflow model (generated by prep_fit)
            feed_dict: information to be passed as input to the Tensorflow model (generated by prep_fit)

        Returns:
            fetches
        """
        return self._run(sess, fetches, feed_dict)

    def predict_feats(self, sess, image_features):
        """
        Take a numpy matrix of image features and predict word vector representation. This differs
        from predict in that this only expects a session and raw image features where as predict
        expects the output of prep_predict
        Args:
            sess: a Tensorflow session
            image_features: numpy matrix of image feature vectors

        Returns:
            predicted features
        """
        return self._run(sess, self.model_info['prediction'], {self.model_info['input']:image_features})

    def predict(self, sess, fetches, feed_dict):
        """
        Function responsible for returning predictions given a fitted Tensorflow session (sess), fetches, and feed_dict.

        Args:
            sess: a Tensorflow session
            fetches: information to be retrieved from the Tensorflow model (usually generated by prep_predict)
            feed_dict: information to be passed as input to the Tensorflow model (usually generated by prep_predict)

        Returns:
            predictions as a numpy array
        """
        return self._run(sess, fetches, feed_dict)

    def prep_fit(self, data):
        """
        Given some data, return a tuple of (fetches, feed_dict), which are the arguments that will be passed to fit().

        Args:
            data: input data

        Returns:
            a tuple of (fetches, feed_dict) that will be passed to fit() and eventually a Tensorflow session
        """
        raise NotImplementedError()

    def prep_predict(self, dataset, cross_eval=False):
        """
        Given some data, return a three tuple: (fetches, feed_dict, truth). The first two will be passed as a tuple to predict(), while truth will be used to evaluate predictions in the Evaluator class

        Args:
            dataset: an Attalos dataset

        Returns:
            a tuple of (fetches, feed_dict) that will be passed to predict() and eventually a Tensorflow session
        """
        raise NotImplementedError()

    def post_predict(self, predict_fetches, cross_eval=False):
        """
        Hook for post processing after predict(). By default, this is a no-op. Subclasses should override this if they have additional post-processing steps for predictions.

        Args:
            predict_fetches: fetches retrieved from Tensorflow model matching fetches returned by prep_predict

        Returns:

        """
        return predict_fetches

    def get_training_loss(self, fit_fetches):
        """
        Extracts training loss only from the fetches specified by prep_fit.

        Args:
            fit_fetches: fetches returned by calling sess.run given input fetches from prep_fit.

        Returns:
            training loss
        """
        raise NotImplementedError()
