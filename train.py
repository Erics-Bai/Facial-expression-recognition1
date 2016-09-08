
import tensorflow as tf
from tflearn import DNN
import time
import argparse

from data_loader import load_data 
from parameters import DATASET, TRAINING, HYPERPARAMS, NETWORK
from model import build_model

def train(optimizer=HYPERPARAMS.optimizer, optimizer_param=HYPERPARAMS.optimizer_param, 
        learning_rate=HYPERPARAMS.learning_rate, keep_prob=HYPERPARAMS.keep_prob, 
        learning_rate_decay=HYPERPARAMS.learning_rate_decay, decay_step=HYPERPARAMS.decay_step):

        print "loading dataset " + DATASET.name + "..."
        data, validation = load_data(validation=True)

        with tf.Graph().as_default():
                print "building model..."
                network = build_model(optimizer, optimizer_param, learning_rate, 
                          keep_prob, learning_rate_decay, decay_step)
                model = DNN(network, tensorboard_dir=TRAINING.logs_dir, 
                        tensorboard_verbose=0, checkpoint_path=TRAINING.checkpoint_dir,
                        max_checkpoints=TRAINING.max_checkpoints)

                #tflearn.config.init_graph(seed=None, log_device=False, num_cores=6)

                print "start training..."
                print "  - optimizer = '{}'".format(optimizer)
                print "  - learning_rate = {}".format(learning_rate)
                print "  - learning_rate_decay = {}".format(learning_rate_decay)
                print "  - otimizer_param ({}) = {}".format('beta1' if optimizer == 'adam' else 'momentum', optimizer_param)
                print "  - keep_prob = {}".format(keep_prob)
                print "  - epochs = {}".format(TRAINING.epochs)
                start_time = time.time()

                if NETWORK.use_landmarks:
                        model.fit([data['X'], data['X2']], data['Y'],
                                validation_set=([validation['X'], validation['X2']], validation['Y']),
                                snapshot_step=TRAINING.snapshot_step,
                                show_metric=TRAINING.vizualize,
                                batch_size=TRAINING.batch_size,
                                n_epoch=TRAINING.epochs)
                else:
                        model.fit(data['X'], data['Y'],
                                validation_set=(validation['X'], validation['Y']),
                                snapshot_step=TRAINING.snapshot_step,
                                show_metric=TRAINING.vizualize,
                                batch_size=TRAINING.batch_size,
                                n_epoch=TRAINING.epochs)
                        validation['X2'] = None
                training_time = time.time() - start_time
                print "training time = {0:.1f} sec".format(training_time)

                if TRAINING.save_model:
                        print "saving model..."
                        model.save(TRAINING.save_model_path)

                print "evaluating..."
                validation_accuracy = evaluate(model, validation['X'], validation['X2'], validation['Y'])
                print "  - accuracy = {0:.1f}".format(validation_accuracy*100)

                return validation_accuracy

def evaluate(model, X, X2, Y):
        if NETWORK.use_landmarks:
                accuracy = model.evaluate([X, X2], Y)
        else:
                accuracy = model.evaluate(X, Y)
        return accuracy[0]

# parse arg to see if we need to launch training now or not yet
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--train", default="no", help="if 'yes', launch training from command line")
parser.add_argument("-m", "--max_evals", help="Maximum number of evaluations during hyperparameters search")
args = parser.parse_args()
if args.train=="yes" or args.train=="Yes" or args.train=="YES":
        train()