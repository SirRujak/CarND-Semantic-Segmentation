import os.path
import tensorflow as tf
from tensorflow import contrib
import helper
import warnings
from distutils.version import LooseVersion
import project_tests as tests


# Check TensorFlow Version
assert LooseVersion(tf.__version__) >= LooseVersion('1.0'), 'Please use TensorFlow version 1.0 or newer.  You are using {}'.format(tf.__version__)
print('TensorFlow Version: {}'.format(tf.__version__))

# Check for a GPU
if not tf.test.gpu_device_name():
    warnings.warn('No GPU found. Please use a GPU to train your neural network.')
else:
    print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))


def load_vgg(sess, vgg_path):
    """
    Load Pretrained VGG Model into TensorFlow.
    :param sess: TensorFlow Session
    :param vgg_path: Path to vgg folder, containing "variables/" and "saved_model.pb"
    :return: Tuple of Tensors from VGG model (image_input, keep_prob, layer3_out, layer4_out, layer7_out)
    """
    # TODO: Implement function
    #   Use tf.saved_model.loader.load to load the model and weights
    vgg_tag = 'vgg16'
    vgg_input_tensor_name = 'image_input:0'
    vgg_keep_prob_tensor_name = 'keep_prob:0'
    vgg_layer3_out_tensor_name = 'layer3_out:0'
    vgg_layer4_out_tensor_name = 'layer4_out:0'
    vgg_layer7_out_tensor_name = 'layer7_out:0'

    tf.saved_model.loader.load(sess, [vgg_tag], vgg_path)
    graph = tf.get_default_graph()
    input_layer = graph.get_tensor_by_name(vgg_input_tensor_name)
    keep_prob = graph.get_tensor_by_name(vgg_keep_prob_tensor_name)
    vgg_l3 = graph.get_tensor_by_name(vgg_layer3_out_tensor_name)
    vgg_l4 = graph.get_tensor_by_name(vgg_layer4_out_tensor_name)
    vgg_l7 = graph.get_tensor_by_name(vgg_layer7_out_tensor_name)
    
    return input_layer, keep_prob, vgg_l3, vgg_l4, vgg_l7
tests.test_load_vgg(load_vgg, tf)


def layers(vgg_layer3_out, vgg_layer4_out, vgg_layer7_out, num_classes):
    """
    Create the layers for a fully convolutional network.  Build skip-layers using the vgg layers.
    :param vgg_layer3_out: TF Tensor for VGG Layer 3 output
    :param vgg_layer4_out: TF Tensor for VGG Layer 4 output
    :param vgg_layer7_out: TF Tensor for VGG Layer 7 output
    :param num_classes: Number of classes to classify
    :return: The Tensor for the last layer of output
    """
    # TODO: Implement function
    ## Atrous pyramid.
    atrous_1 = tf.layers.conv2d(vgg_layer7_out, 128, 1, padding="same", dilation_rate=(1, 1),
                                                    kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3), name="atrous_1x1")
    atrous_2 = tf.layers.conv2d(vgg_layer7_out, 128, 1, padding="same", dilation_rate=(5, 5),
                                                    kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3), name="atrous_3x3")
    atrous_3 = tf.layers.conv2d(vgg_layer7_out, 128, 1, padding="same", dilation_rate=(7, 7),
                                                    kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3), name="atrous_12x12")
    atrous_4 = tf.layers.conv2d(vgg_layer7_out, 128, 1, padding="same", dilation_rate=(12, 12),
                                                    kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3), name="atrous_18x18")
    atrous_5 = tf.layers.conv2d(vgg_layer7_out, 128, 1, padding="same", name="atrous_pool")

    atrous_pyramid = tf.concat([atrous_1, atrous_2, atrous_3, atrous_4, atrous_5], -1, name="atrous_pyramid")
    #atrous_pyramid = atrous_1 + atrous_2 + atrous_3 + atrous_4 + atrous_5
    atrous_pyramid = tf.layers.conv2d(vgg_layer7_out, 128, 1, padding="same",
                                                    kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    atrous_expanded = tf.layers.conv2d_transpose(atrous_pyramid, 128, 2, 2, padding="same",
                                                    kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3), name="atrous_expanded")

    vgg_layer4_1x1 = tf.layers.conv2d(vgg_layer4_out, 128, 1,
                                                    kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3), padding="same")
    #add_1 = tf.concat([atrous_expanded, vgg_layer4_1x1], -1, name="add_1")
    add_1 = atrous_expanded + vgg_layer4_1x1
    output_2 = tf.layers.conv2d_transpose(add_1, 64, 4, 2, padding="same",
                                                    kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3), name="output_2")

    vgg_layer3_1x1 = tf.layers.conv2d(vgg_layer3_out, 64, 1, padding="same")
    #add_2 = tf.concat([output_2, vgg_layer3_1x1], -1, name="add_2")
    add_2 = output_2 + vgg_layer3_1x1
    output_3_1 = tf.layers.conv2d_transpose(add_2, 32, 2, 2, padding="same",
                                                    kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3), name="output_3")
    output_3_2 = tf.layers.conv2d_transpose(output_3_1, 16, 2, 2, padding="same",
                                                    kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3), name="output_4")
    final_output = tf.layers.conv2d_transpose(output_3_2, num_classes, 4, 2, padding="same",
                                                    kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3), name="output_5")

    return final_output
    
    #return conv_3x3
    #return vgg_layer7_out
tests.test_layers(layers)


def optimize(nn_last_layer, correct_label, learning_rate, num_classes):
    """
    Build the TensorFLow loss and optimizer operations.
    :param nn_last_layer: TF Tensor of the last layer in the neural network
    :param correct_label: TF Placeholder for the correct label image
    :param learning_rate: TF Placeholder for the learning rate
    :param num_classes: Number of classes to classify
    :return: Tuple of (logits, train_op, cross_entropy_loss)
    """
    # TODO: Implement function
    ##logits = tf.reshape(nn_last_layer, (-1, num_classes))
    logits = nn_last_layer
    cross_entropy_loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=correct_label), name="cross_ent_loss")
    regularizer_losses = tf.losses.get_regularization_loss()
    normalizer = tf.constant(1.2)
    total_loss = cross_entropy_loss + regularizer_losses * normalizer
    #train_op = tf.contrib.opt.NadamOptimizer().minimize(total_loss)
    train_op = tf.train.AdamOptimizer().minimize(total_loss)
    return logits, train_op, total_loss
tests.test_optimize(optimize)


def train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image,
             correct_label, keep_prob, learning_rate):
    """
    Train neural network and print out the loss during training.
    :param sess: TF Session
    :param epochs: Number of epochs
    :param batch_size: Batch size
    :param get_batches_fn: Function to get batches of training data.  Call using get_batches_fn(batch_size)
    :param train_op: TF Operation to train the neural network
    :param cross_entropy_loss: TF Tensor for the amount of loss
    :param input_image: TF Placeholder for input images
    :param correct_label: TF Placeholder for label images
    :param keep_prob: TF Placeholder for dropout keep probability
    :param learning_rate: TF Placeholder for learning rate
    """
    # TODO:? Implement function

    for epoch in range(epochs):
        print("Begin epoch: {}:".format(epoch))
        counter = 0
        average_loss = 0
        for image, label in get_batches_fn(batch_size):
            counter += batch_size
            feed_dict = {input_image:image, correct_label:label, keep_prob:0.5, learning_rate:0.001}
            _, loss = sess.run((train_op, cross_entropy_loss), feed_dict=feed_dict)
            average_loss += loss
            #print(counter)
            #print(loss)

            if counter % 10 == 0:
                print("Current loss:, {}. Average loss for set: {}.".format(loss * 1.0/batch_size, average_loss * 1.0/counter))
                #average_loss = 0
        print("Epoch complete:\nCurrent loss:, {}. Average loss for set: {}.".format(loss * 1.0/batch_size, average_loss * 1.0/counter))
tests.test_train_nn(train_nn)


def run():
    num_classes = 3
    image_shape = (160, 576)
    data_dir = './data'
    runs_dir = './runs'
    tests.test_for_kitti_dataset(data_dir)

    # Download pretrained vgg model
    helper.maybe_download_pretrained_vgg(data_dir)

    # OPTIONAL: Train and Inference on the cityscapes dataset instead of the Kitti dataset.
    # You'll need a GPU with at least 10 teraFLOPS to train on.
    #  https://www.cityscapes-dataset.com/

    with tf.Session() as sess:
        # Path to vgg model
        print("Loading data...")
        vgg_path = os.path.join(data_dir, 'vgg')
        # Create function to get batches
        get_batches_fn = helper.gen_batch_function(os.path.join(data_dir, 'data_road/training'), image_shape)
        print("Data loaded...")

        # OPTIONAL: Augment Images for better results
        #  https://datascience.stackexchange.com/questions/5224/how-to-prepare-augment-images-for-neural-network

        # TODO: Build NN using load_vgg, layers, and optimize function
        "Building network..."
        input_image, keep_prob, vgg_l3, vgg_l4, vgg_l7 = load_vgg(sess, vgg_path)
        output_layer = layers(vgg_l3, vgg_l4, vgg_l7, num_classes)

        correct_label = tf.placeholder(tf.float32, (None, None, None, num_classes), name="correct_label")
        learning_rate = tf.Variable(0.001, name="learning_rate", dtype=tf.float32)
        logits, train_op, loss = optimize(output_layer, correct_label, learning_rate, num_classes)
        "Network built..."

        # TODO:? Train NN using the train_nn function
        print("Initializing network...")
        epochs = 12
        batch_size = 8

        init_op = tf.global_variables_initializer()
        saver = tf.train.Saver()
        sess.run(init_op)
        print("Network initialized...")

        print("Training network...")
        train_nn(sess, epochs, batch_size, get_batches_fn, train_op, loss, input_image, correct_label, keep_prob, learning_rate)
        print("Network trained...")


        ## Save the network here.
        save_path = saver.save(sess, "data/models/final_model")

        # TODO:? Save inference data using helper.save_inference_samples
        #  helper.save_inference_samples(runs_dir, data_dir, sess, image_shape, logits, keep_prob, input_image)
        helper.save_inference_samples(runs_dir, data_dir, sess, image_shape, logits, keep_prob, input_image)
        print("Saved")

        # OPTIONAL: Apply the trained model to a video


if __name__ == '__main__':
    run()
