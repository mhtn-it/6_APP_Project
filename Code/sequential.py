import numpy as np
import cv2
import os
import scipy
from  scipy import ndimage
from numba import jit
IMAGES_FOLDER_PATH = "../Data/Input"

def calc_masks(tri, img_gray):
    """
    Hàm tạo mask để phân vùng Background và Foreground của ảnh trimap

    Parameters:
    -----------
    tri: mảng numpy đại diện cho ảnh trimap ở dạng grayscale
    img_gray: mảng numpy đại điện cho ảnh phiên bản grayscale

    Return:
    -----------
    Danh sách các mảng numpy đại diện cho: foreground mask, foreground image, background mask,
    background image, unknown region mask,unknown region image
    """
    mask_bg = (tri<10)
    mask_fg = (tri>245)
    mask_unknown = (np.bitwise_and(tri>=10,tri<=245))

    fg = img_gray*(mask_fg)
    bg = img_gray*(mask_bg)
    unknown = img_gray*mask_unknown
    return [mask_fg,fg,mask_bg,bg,mask_unknown,unknown], ['fg mask','fg','bg mask','bg','mask unknown','unkown reg img']

def doubleDifferential(img, factor):
    """
    Hàm tính đạo hàm bậc hai phục vụ cho phương trình Poisson

    Parameters:
    -----------
    img: mảng numpy đại diện cho ảnh inpu grayscale
    factor: một hằng số dùng để chia vi phân cấp nhất trước khi tính vi phân cấp 2. 
            Factor có thể là một hằng hoặc một mảng numpy bằng kích thước của ảnh.

    Return:
    -----------
    Hai mảng numpy đại điện cho vi phân cấp hai tương ứng với Y và X.
    """
    dy, dx = np.gradient(img)
    d2y, _ = np.gradient(dy/factor)
    _, d2x = np.gradient(dx/factor)
    return d2y, d2x

def fb(img_gray,mask_fg,mask_bg,mask_unknown):
    """
    Hàm tìm xấp xỉ vùng Background và Foreground

    Parameters:
    -----------
    img_gray,mask_fg,mask_bg,mask_unknown: lần lượt là mảng numpy đại diện cho ảnh input grayscale,
                                           vùng Foreground, vùng Background, vùng chưa xác định

    Return:
    -----------
    Hai mảng numpy đại điện cho xấp xỉ vùng Background và Foreground.
    """
    F = img_gray*(mask_fg+mask_unknown)
    B = img_gray*(mask_bg+mask_unknown)
    return F, B

def global_alpha_matting(alpha, d2alpha, unknown_seg,iters = 50, threshold = 0.1, beta = 1):
    """
    Hàm thực thi global alpha matting

    Parameters:
    -----------
    alpha: giá trị xấp xỉ của alpha
    d2alpha: tổng đạo hàm riêng bậc 2 của alpha theo X và Y
    unknown_seg: mảng munby đại diện cho vùng chưa xác định rõ
    iters: số lần chạy của phương pháp ước lượng Gauss Siedel
    threshold: ngưỡng cho sự thay đổi sau mỗi lần chạy. Nếu dưới ngưỡng thì phương trình sẽ dừng lại
    beta: nhân tử beta của phương pháp ước lượng Gauss Siedel

    Return:
    -----------
    Mảng numpy đại diện cho chỉ số matte đã được tạo và thời gian thực thi
    """
    prev_alpha = np.zeros(alpha.shape)
    diff = np.sum(np.abs(prev_alpha-alpha))
    
    for _ in range(iters):
        diff = np.sum(np.abs(prev_alpha-alpha))
        if diff < threshold:
            break
        for i in range(1,alpha.shape[0]-1):
            for j in range(1,alpha.shape[1]-1):
                if unknown_seg[i,j]!=0 :
                    alpha[i,j] = ((beta*(alpha[i,j-1]+alpha[i-1,j]+prev_alpha[i,j+1]+prev_alpha[i+1,j] - d2alpha[i,j])/4) + (1-beta)*prev_alpha[i,j])
    return alpha

def grads(F,B,mask_fg,img_gray,mask_unknown):
    """
    Hàm tính Gradient của ảnh input

    Parameters:
    -----------
    F,B,mask_fg,img_gray,mask_unknown: lần lượt là mảng numpy đại diện cho vùng xấp xỉ của Foreground, 
                                        Background, mask fg, ảnh input grayscale, mask_unknow

    Return:
    -----------
    Mảng numpy đại diện cho xấp xỉ alpha
    Mảng numpy đại diện cho đạo hàm bậc hai của alpha
    Mảng numby đại diện cho sự khác nhau của xấp xỉ giữa Foreground và Background
    """
    diff = np.minimum(np.maximum(F-B,0),255)

    diff = ndimage.filters.gaussian_filter(diff, 0.9)
    diff = np.minimum(np.maximum(diff,0),255)
    grad_y,grad_x = np.gradient(img_gray)
    diff[diff==0] = 1
    d2y_alpha, _ = np.gradient(grad_y/diff)
    _, d2x_alpha = np.gradient(grad_x/diff)
    d2alpha = d2y_alpha + d2x_alpha
    estimate_alpha = mask_fg + 0.5*mask_unknown
    return estimate_alpha, d2alpha, diff

def func_estimate_alpha(tri, img_gray):
    """
    Hàm tính xấp xỉ alpha

    Parameters:
    -----------
    tri: ảnh trimap
    img_grayscale: ảnh input ở phiên bản grayscale

    Return:
    -----------
    Xấp xỉ alpha, Foreground, BackGround, đạo hàm bậc 2 của alpha, 
    Danh sách các biến đầu vào đã xử lý của input, sự khác biệt của F và B
    """
    imgs, titles = calc_masks(tri, img_gray)
    mask_fg,fg,mask_bg,bg,mask_unknown,unknown = imgs
    
    F,B = fb(img_gray,mask_fg,mask_bg,mask_unknown)
    est_alpha, d2alpha, diff =  grads(F,B,mask_fg,img_gray,mask_unknown)
    return est_alpha, F, B, d2alpha, imgs, diff

def matting_combined(tri, img_gray):
    """
    Hàm tổng hợp bước matting

    Parameters:
    -----------
    tri: ảnh trimap
    img_gray: ảnh input dạng grayscale

    Return:
    -----------
    Một từ điển chứa thông tin về matting của bức ảnh: alpha, F, B, diff, vùng chưa xác định, vùng chưa xác định của trimap
    """
    estimate_alpha, F, B, d2alpha, imgs, diff = func_estimate_alpha(tri, img_gray)
    mask_fg,fg,mask_bg,bg,mask_unknown,unknown = imgs
    alpha = global_alpha_matting(estimate_alpha,d2alpha,mask_unknown)
    alpha = np.minimum(np.maximum(alpha,0),1)

    return {'alpha': alpha, 'F':F, 'B': B, 'diff': diff, 'unknown': unknown, 'mask_unknown': mask_unknown}

def alpha_blend(new_bg,alpha,img):
    """
    Hàm thực thi alpha_blend

    Parameters:
    -----------
    new_bg: một mảng numpy đại diện cho background mới (có màu)
    alpha: mảng numpy đại diện cho các chỉ số alpha dùng để matte
    img: bức ảnh gốc

    Return:
    -----------
    Một bức ảnh mới đã đổi background
    """
    new_img = np.zeros(new_bg.shape)
    new_img[:,:,0] = alpha*img[:,:,0] + (1-alpha)*new_bg[:,:,0]
    new_img[:,:,1] = alpha*img[:,:,1] + (1-alpha)*new_bg[:,:,1]
    new_img[:,:,2] = alpha*img[:,:,2] + (1-alpha)*new_bg[:,:,2]
    return np.float32(new_img)

def local_matting(data_dic, top, bottom, left, right):
    """
    Hàm Local Matting sử dụng Matte do Global Matting cung cấp và 
    tọa độ do người dùng cung cấp để cải thiện khả năng xử lý.

    Parameters:
    -----------
    data_dic: Một dict chứa các hình ảnh khác nhau được tính toán trong khi thực hiện global matting.
    top: Giá trị cho điểm phía trên của ROI
    bottom: Giá trị cho điểm phía dưới của ROI
    left: Giá trị cho điểm bên trái của ROI
    right: Giá trị cho điểm bên phải của ROI
    
    Return:
    -----------
    matte: Mảng giá trị alpha sau khi Local Matting
    """
    h, w = data_dic['alpha'].shape[0], data_dic['alpha'].shape[1]
    local = 0
    if('local_matte' in data_dic.keys()):
        local = 1
        h, w = data_dic['local_matte'].shape[0], data_dic['local_matte'].shape[1]
        
    new_diff = data_dic['diff'][top:bottom+1, left:right+1]
    
    ## APPLYING GAUSSIAN FILTER ON THIS NEW DIFF
    new_diff = ndimage.filters.gaussian_filter(new_diff, 0.9)
    new_diff = np.minimum(np.maximum(new_diff,0),255)
    
    ## EXTRACTING SEGMENTS IN GIVEN RANGE FOR ORIGINAL IMAGE, FOREGROUND AND THE BACKGROUND
    required_img= data_dic['img_gray'].copy()[top:bottom+1, left:right+1]
    required_fg = data_dic['F'].copy()[top:bottom+1,left:right+1]
    required_bg = data_dic['B'].copy()[top:bottom+1,left:right+1]
    required_unknown = data_dic['unknown'].copy()[top:bottom,left:right]
    required_alpha= data_dic['alpha'].copy()[top:bottom+1,left:right+1]
    if(local==1):
        required_alpha= data_dic['local_matte'].copy()[top:bottom+1,left:right+1]
    
    required_inverted_alpha= 1 - required_alpha
    required_mask_unknown = data_dic['mask_unknown'].copy()[top:bottom+1, left:right+1]
    
    ## GET DOUBLE DIFFERENTIAL FOR IMG, FOREGROUND AND BACKGROUND
    fg_d2y, fg_d2x = doubleDifferential(required_fg, new_diff)
    bg_d2y, bg_d2x = doubleDifferential(required_bg, new_diff)
    img_d2y, img_d2x = doubleDifferential(required_img, new_diff)
    weighted_fg = required_alpha*(fg_d2x+fg_d2y)
    weighted_bg = required_alpha*(bg_d2x+bg_d2y)
    new_d2alpha = img_d2x + img_d2y - weighted_fg - weighted_bg

    matte = global_alpha_matting(required_alpha,new_d2alpha,required_mask_unknown, iters= 50, threshold = 0.1, beta = 0.2)
    matte = np.minimum(np.maximum(matte,0),1)
    return matte

img = cv2.imread(os.path.join(IMAGES_FOLDER_PATH, 'input_4.png'))
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_gray = cv2.imread(os.path.join(IMAGES_FOLDER_PATH, 'input_4.png'),0)
tri = cv2.imread(os.path.join(IMAGES_FOLDER_PATH, 'input_4_tri.png'),0)

new_bg = cv2.imread(os.path.join(IMAGES_FOLDER_PATH, 'background3.jpg'))
new_bg = cv2.cvtColor(new_bg, cv2.COLOR_BGR2RGB)
new_bg = cv2.resize(new_bg, (img.shape[1],img.shape[0])) 

all_data = matting_combined(tri, img_gray)

# Bổ sung loại hình ảnh vào all_data
all_data.update({'img': img, 'img_gray': img_gray})

alpha = all_data['alpha']
new_img_global = alpha_blend(new_bg,alpha,img)

new_img_global = cv2.cvtColor(new_img_global, cv2.COLOR_RGB2BGR)
cv2.imwrite('../Data/Output/output_4_global.png', new_img_global)

all_data_2 = all_data.copy()
local_matte =  all_data_2['alpha'].copy()
top,bottom,left,right = [347, 475, 130, 195]
local_matte[top:bottom+1, left:right+1] = local_matting(all_data_2.copy(), top, bottom, left, right)
all_data_2['local_matte'] = local_matte
top,bottom,left,right = [367, 480, 386, 439]
local_matte[top:bottom+1, left:right+1] = local_matting(all_data_2.copy(), top, bottom, left, right)
all_data_2['local_matte'] = local_matte
local_matte = np.minimum(np.maximum(local_matte,0),1)

new_img_local = alpha_blend(new_bg,local_matte,img)

new_img_local = cv2.cvtColor(new_img_local, cv2.COLOR_RGB2BGR)
cv2.imwrite('../Data/output/output_4_local.png', new_img_local)

