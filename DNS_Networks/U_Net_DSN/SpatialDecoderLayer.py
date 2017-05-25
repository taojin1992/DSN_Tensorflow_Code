import tensorflow as tf
import time
import datetime
sess = tf.Session()
class inverse_transformer(object):
	def __init__(self,U,Column_controlP_number,Row_controlP_number,out_size):
		self.num_batch = U.shape[0].value
		self.height = U.shape[1].value
		self.width = U.shape[2].value
		self.num_channels = U.shape[3].value
		self.out_height = self.height
		self.out_width = self.width
		self.out_size = out_size
		self.Column_controlP_number = Column_controlP_number
		self.Row_controlP_number = Row_controlP_number

	def _repeat(self,x, n_repeats, type):
		with tf.variable_scope('_repeat'):
			rep = tf.transpose(
			    tf.expand_dims(tf.ones(shape=tf.stack([n_repeats, ])), 1), [1, 0])
			rep = tf.cast(rep, type)
			x = tf.matmul(tf.reshape(x, (-1, 1)), rep)
			return tf.reshape(x, [-1])

	def _bilinear_interpolate(self,im, im_org, x, y, out_size):
		with tf.variable_scope('_interpolate'):
            # constants
<<<<<<< HEAD
            num_batch = im.shape[0].value
            height = im.shape[1].value
            width = im.shape[2].value
            channels = im.shape[3].value
            A_U,B_U,C_U,D_U = _split_input(im,width,height)
            x = tf.cast(x, 'float32')
            y = tf.cast(y, 'float32')
            height_f = tf.cast(height, 'float32')
            width_f = tf.cast(width, 'float32')
            out_height = height
            out_width = width
            zero = tf.zeros([], dtype='int32')
            max_y = tf.cast(im.shape[1].value - 1, 'int32')
            max_x = tf.cast(im.shape[2].value - 1, 'int32')
            # scale indices from [-1, 1] to [0, width/height]
            x = (x + 1.0)*(width_f) / 2.0
            y = (y + 1.0)*(height_f) / 2.0
            X = tf.reshape(x,[num_batch,height,width,channels])
            Y = tf.reshape(y,[num_batch,height,width,channels])
            # get A B C D coordinate
            Ax,Bx,Cx,Dx = _split_input(X,width,height)
            Ay,By,Cy,Dy = _split_input(Y,width,height)
            # get min coordinate
            Min_X = tf.minimum(tf.minimum(Ax,Bx),tf.minimum(Cx,Dx))
            Min_Y = tf.minimum(tf.minimum(Ay,By),tf.minimum(Cy,Dy))
            #get max coordinate
            Max_X = tf.maximum(tf.maximum(Ax,Bx),tf.maximum(Cx,Dx))
            Max_Y = tf.maximum(tf.maximum(Ay,By),tf.maximum(Cy,Dy))
            Px_min = tf.cast(tf.minimum(tf.maximum(tf.ceil(Min_X),0),width-1),'int32')
            Py_min = tf.cast(tf.minimum(tf.maximum(tf.ceil(Min_Y),0),height-1),'int32')
            Px_max = tf.cast(tf.maximum(tf.minimum(tf.floor(Max_X),width-1),0),'int32')
            Py_max = tf.cast(tf.maximum(tf.minimum(tf.floor(Max_Y),width-1),0),'int32')
            PX = Px_min
            PY = Py_min
            #final Value from U
            Value_from_U_final = tf.zeros([num_batch,height*width*channels])
            Value_from_U_final = tf.cast(Value_from_U_final,'float32')
            Weights = tf.zeros([num_batch,height*width*channels])
            gap_x = tf.zeros_like(PX)
            gap_y = tf.zeros_like(PY)
            for i in range(4):
                PX = PX + gap_x
                PY = PY + gap_y
                Px = tf.cast(PX,'float32')
                Py = tf.cast(PY,'float32')
                Value_ABC,weight_ABC = _triange_function(Px,Py,Ax,Ay,Bx,By,Cx,Cy,A_U,B_U,C_U)
                Value_BCD,weight_BCD = _triange_function(Px,Py,Dx,Dy,Bx,By,Cx,Cy,D_U,B_U,C_U)
                Value_ACD,weight_ACD = _triange_function(Px,Py,Ax,Ay,Dx,Dy,Cx,Cy,A_U,D_U,C_U)
                Value_ABD,weight_ABD = _triange_function(Px,Py,Ax,Ay,Bx,By,Dx,Dy,A_U,B_U,D_U)
                Weight_all = tf.clip_by_value(weight_ABC + weight_BCD + weight_ACD + weight_ABD,0.001,1e+10)
                Value_final =  (Value_ABC+Value_BCD + Value_ACD + Value_ABD)/Weight_all
                coordx= tf.cast(tf.reshape(Px,[-1]),'int32')
                coordy = tf.cast(tf.reshape(Py,[-1]),'int32')
                dim2 = width
                dim1 = width*height
                Base = _repeat(tf.range(channels)*dim1, (out_height)*(out_width))
                Base = tf.tile(Base,tf.stack([num_batch]))
                Base = tf.reshape(Base,[num_batch,height,width,channels])
                Base,_,_,_ = _split_input(Base,height,width)
                Base = tf.reshape(Base,[-1])
                Base_Y = Base + coordy*dim2
                coordinate = Base_Y + coordx
                coordinate = tf.expand_dims(coordinate,0)
                #get batch index
                batch_index = []
                for i in range(num_batch):
                    batch_index.append(i)
                batch_index = tf.transpose(tf.expand_dims(tf.stack(batch_index),0))
                batch_index = tf.cast(batch_index,tf.int32)
                batch_index = tf.reshape(tf.tile(batch_index,[1,(height-1)*(width-1)*channels]),[-1,1])
                #get corresponding image coordinate
                coordinate = tf.reshape(coordinate,[-1,1])  
                Index = tf.concat([batch_index,coordinate],1)  
                Index = tf.cast(Index,tf.int64)
                #Im
                #Value from U
                Value_final=tf.reshape(Value_final,[num_batch*(height-1)*(width-1)*channels])
                sparse_values=tf.SparseTensor(indices=Index, values=Value_final, dense_shape=[num_batch,height*width*channels])
                Value_from_U=tf.sparse_tensor_to_dense(sp_input=sparse_values,default_value=-10,validate_indices=False)
                Value_from_U=tf.cast(Value_from_U,'float32')
                #weights
                thred=tf.subtract(tf.ones_like(Value_from_U,'float32'),8)
                weights=tf.Tensor.__ge__(Value_from_U,thred)
                weights=tf.cast(weights,tf.float32)
                Weights += weights
                Value_from_U_final+=Value_from_U
                gap_x = tf.less(0,Px_max-PX)
                gap_y = tf.less(0,Py_max-PY)
                gap_x = tf.cast(gap_x,'int32')
                gap_y = tf.cast(gap_y,'int32')
            #Weights=tf.cast(Weights,'float32')
            Value_from_U_final = Value_from_U_final/Weights
            Thred=tf.subtract(tf.ones_like(Value_from_U_final,'float32'),8)
            #Check which state is selected
            S_o_r_bool=tf.Tensor.__ge__(Value_from_U_final,Thred)
            S_o_r_value=tf.cast(S_o_r_bool,tf.float32)
            S_o_r_value=tf.subtract(tf.ones_like(S_o_r_value),S_o_r_value)
            #Value from im_org
            b_org = tf.shape(im_org)[0]
            im_org=tf.reshape(im_org,[b_org,-1])
            im_org = tf.cast(im_org,'float32')
            Value_from_im_org = tf.multiply(S_o_r_value,im_org) 
            #Use to offset the thred value
            Equal_to_thred=tf.multiply(S_o_r_value,10) 
            #Ouput value
            output = tf.add(tf.add(Value_from_U_final,Value_from_im_org),Equal_to_thred)
            return output
        
    def _meshgrid(U,height, width,Column_controlP_number,Row_controlP_number):
        with tf.variable_scope('_meshgrid'):
            num_batch = U.shape[0].value
            height = U.shape[1].value
            width = U.shape[2].value
            channels = U.shape[3].value
            x_t = tf.matmul(tf.ones(shape=tf.stack([height, 1])),
                            tf.transpose(tf.expand_dims(tf.linspace(-1.0, 1.0, width), 1), [1, 0]))
            y_t = tf.matmul(tf.expand_dims(tf.linspace(-1.0, 1.0, height), 1),
                            tf.ones(shape=tf.stack([1, width])))
=======
			x = tf.cast(x, 'float32')
			y = tf.cast(y, 'float32')
			height_f = tf.cast(self.height, 'float32')
			width_f = tf.cast(self.width, 'float32')
			zero = tf.zeros([], dtype='int32')
			max_y = tf.cast(tf.shape(im)[1] - 1, 'int32')
			max_x = tf.cast(tf.shape(im)[2] - 1, 'int32')
			# scale indices from [-1, 1] to [0, width/height]
			x = (x + 1.0)*(width_f) / 2.0
			y = (y + 1.0)*(height_f) / 2.0
			# do sampling
			print(sess.run(tf.shape(im)))
			x0 = tf.cast(tf.floor(x), 'int32')
			x1 = x0 + 1
			y0 = tf.cast(tf.floor(y), 'int32')
			y1 = y0 + 1
			x0 = tf.clip_by_value(x0, zero, max_x)
			x1 = tf.clip_by_value(x1, zero, max_x)
			y0 = tf.clip_by_value(y0, zero, max_y)
			y1 = tf.clip_by_value(y1, zero, max_y)
			dim2 = self.width
			dim1 = self.width*self.height
			base = self._repeat(tf.range(self.num_batch)*dim1, self.out_height*self.out_width, 'int32')
			print(sess.run(tf.shape(base)))
			base_y0 = base + y0*dim2
			base_y1 = base + y1*dim2
			idx_a = tf.expand_dims(base_y0 + x0, 1)
			idx_b = tf.expand_dims(base_y1 + x0, 1)
			idx_c = tf.expand_dims(base_y0 + x1, 1)
			idx_d = tf.expand_dims(base_y1 + x1, 1)
			# use indices to lookup pixels in the flat image and restore
			# channels dim
			im_flat = tf.reshape(im, tf.stack([-1, self.num_channels]))
			im_flat = tf.cast(im_flat, 'float32')
			Ia = tf.scatter_nd(idx_a, im_flat, [self.num_batch*self.out_height*self.out_width, self.num_channels])
			Ib = tf.scatter_nd(idx_b, im_flat, [self.num_batch*self.out_height*self.out_width, self.num_channels])
			Ic = tf.scatter_nd(idx_c, im_flat, [self.num_batch*self.out_height*self.out_width, self.num_channels])
			Id = tf.scatter_nd(idx_d, im_flat, [self.num_batch*self.out_height*self.out_width, self.num_channels])

			x0_f = tf.cast(x0, 'float32')
			x1_f = tf.cast(x1, 'float32')
			y0_f = tf.cast(y0, 'float32')
			y1_f = tf.cast(y1, 'float32')
			wa = tf.scatter_nd(idx_a, tf.expand_dims(((x1_f-x) * (y1_f-y)), 1), [self.num_batch*self.out_height*self.out_width, 1])
			wb = tf.scatter_nd(idx_b, tf.expand_dims(((x1_f-x) * (y-y0_f)), 1), [self.num_batch*self.out_height*self.out_width, 1])
			wc = tf.scatter_nd(idx_c, tf.expand_dims(((x-x0_f) * (y1_f-y)), 1), [self.num_batch*self.out_height*self.out_width, 1])
			wd = tf.scatter_nd(idx_d, tf.expand_dims(((x-x0_f) * (y-y0_f)), 1), [self.num_batch*self.out_height*self.out_width, 1])

			value_all = tf.add_n([wa*Ia, wb*Ib, wc*Ic, wd*Id])
			weight_all = tf.clip_by_value(tf.add_n([wa, wb, wc, wd]),1e-5,1e+10)
			flag = tf.less_equal(weight_all, 1e-5* tf.ones_like(weight_all))
			flag = tf.cast(flag, tf.float32)
			im_org = tf.reshape(im_org, [-1,self.num_channels])
			output = tf.add(tf.div(value_all, weight_all), tf.multiply(im_org, flag))
			return output

	def _meshgrid(self,U,height, width):
		with tf.variable_scope('_meshgrid'):
			#initial
			#generate output coordinate
			x_t = tf.matmul(tf.ones(shape=tf.stack([height, 1])),
			                tf.transpose(tf.expand_dims(tf.linspace(-1.0, 1.0, width), 1), [1, 0]))
			y_t = tf.matmul(tf.expand_dims(tf.linspace(-1.0, 1.0, height), 1),
			                tf.ones(shape=tf.stack([1, width])))
			x_t_flat = tf.reshape(x_t, (1, -1))
			y_t_flat = tf.reshape(y_t, (1, -1))
			px,py = tf.stack([x_t_flat],axis=2),tf.stack([y_t_flat],axis=2)
			#source control points
			x,y = tf.linspace(-1.,1.,self.Column_controlP_number),tf.linspace(-1.,1.,self.Row_controlP_number)
			x,y = tf.meshgrid(x,y)
			xs,ys = tf.transpose(tf.reshape(x,(-1,1))),tf.transpose(tf.reshape(y,(-1,1)))
			cpx,cpy = tf.transpose(tf.stack([xs],axis=2),perm=[1,0,2]),tf.transpose(tf.stack([ys],axis=2),perm=[1,0,2])
			px, cpx = tf.meshgrid(px,cpx);py, cpy = tf.meshgrid(py,cpy)
			#Compute distance R
			Rx,Ry = tf.square(tf.subtract(px,cpx)),tf.square(tf.subtract(py,cpy))
			R = tf.add(Rx,Ry)
			R = tf.multiply(R,tf.log(tf.clip_by_value(R,1e-10,1e+10)))
			#Source coordinates
			ones = tf.ones_like(x_t_flat) 
			grid = tf.concat([ones, x_t_flat, y_t_flat,R],0)
			grid = tf.reshape(grid,[-1])
			#grid = _repeat(grid,channels,'float32')
			grid = tf.reshape(grid,[self.Column_controlP_number*self.Row_controlP_number+3,height*width])
			return grid

	def _transform(self, T, U, U_org):
		with tf.variable_scope('_transform'):
			T = tf.reshape(T, (-1, 2, self.Column_controlP_number*self.Row_controlP_number+3))
			T = tf.cast(T, 'float32')
			# grid of (x_t, y_t, 1), eq (1) in ref [1]
			# 19 * (H * W )
			grid = self._meshgrid(U, self.out_height, self.out_width)
			grid = tf.expand_dims(grid, 0)
			#print('grid',sess.run(grid))
			grid = tf.reshape(grid, [-1])
			## B * (19 * H * W)
			grid = tf.tile(grid, tf.stack([self.num_batch]))
			grid = tf.reshape(grid, tf.stack([self.num_batch, self.Column_controlP_number*self.Row_controlP_number+3, -1]))
			T_g = tf.matmul(T, grid)
			# x = B * 1 * (H * W)
			x_s = tf.slice(T_g, [0, 0, 0], [-1, 1, -1])
			y_s = tf.slice(T_g, [0, 1, 0], [-1, 1, -1])
			#print('x_s', sess.run(x_s))
			x_s_flat = tf.reshape(x_s, [-1])
			y_s_flat = tf.reshape(y_s, [-1])
			output_transformed = self._bilinear_interpolate(U,U_org,x_s_flat,y_s_flat,self.out_size)
			output = tf.reshape(output_transformed, tf.stack([self.num_batch, self.out_height, self.out_width, self.num_channels]))
			return output
			
	def TPS_decoder(self,U, U_org, T,name='SpatialDecoderLayer', **kwargs):
		with tf.variable_scope(name):
			output = self._transform(T, U, U_org)
			return output


>>>>>>> feature_OPT



