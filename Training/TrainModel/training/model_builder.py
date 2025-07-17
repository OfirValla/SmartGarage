import tensorflow as tf
from .data_generator import IMAGE_SIZE

def create_model(num_classes_gate, num_classes_parking):
    """Create and compile a new model."""
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=IMAGE_SIZE + (3,),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False  # Fine-tune later if you wish

    x = tf.keras.layers.GlobalAveragePooling2D()(base_model.output)
    x = tf.keras.layers.Dropout(0.2)(x)

    gate_output = tf.keras.layers.Dense(num_classes_gate, activation='softmax', name='gate_output')(x)
    parking_output = tf.keras.layers.Dense(num_classes_parking, activation='softmax', name='parking_output')(x)

    model = tf.keras.Model(inputs=base_model.input, outputs=[gate_output, parking_output])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss={
            'gate_output': 'sparse_categorical_crossentropy',
            'parking_output': 'sparse_categorical_crossentropy'
        },
        metrics={
            'gate_output': 'accuracy',
            'parking_output': 'accuracy'
        }
    )
    
    model.summary()

    return model 