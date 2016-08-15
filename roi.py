# encoding: utf-8


def select_candidates(rois):
    candidates = []
    rois.sort(key=lambda x: x[2] * x[3])
    for i, roi in enumerate(rois):
        if i == 0:
            candidates.append(roi)
        else:
            cnt = 0
            for c in candidates:
                if roi_comp(c, roi):
                    cnt += 1
                else:
                    break
            if cnt == len(candidates):
                candidates.append(roi)
    return candidates


def roi_check_overlap(r1, r2):
    if r1[0] < r2[0]:
        if r1[0] + r1[2] < r2[0]:
            return False
        else:
            if r1[1] < r2[1]:
                if r1[1] + r1[3] < r2[1]:
                    return False
    else:
        if r2[0] + r2[2] < r1[0]:
            return False
        else:
            if r1[1] + r1[3] < r2[1]:
                return False
    return True


def roi_overlap_size(r1, r2):
    if r1[0] < r2[0]:
        # r1 is left to r2
        if r1[0] + r1[2] < r2[0] + r2[2]:
            # r1 and r2 intersects each other horizontally
            overlap_w = r1[0] + r1[2] - r2[0]
        else:
            # r2 is included in r1 horizontally
            overlap_w = r2[2]
    else:
        # r1 is right to r2
        if r2[0] + r2[2] < r1[0] + r1[2]:
            # r1 and r2 intersects each other horizontally
            overlap_w = r2[0] + r2[2] - r1[0]
        else:
            # r1 is included in r2 horizontally
            overlap_w = r1[2]

    if r1[1] < r2[1]:
        # r1 is above to r2
        if r1[1] + r1[3] < r2[1] + r2[3]:
            # r1 and r2 intersects each other vertically
            overlap_h = r1[1] + r1[3] - r2[1]
        else:
            # r2 is included in r1 vertically
            overlap_h = r2[3]
    else:
        # r1 is below to r2
        if r2[1] + r2[3] < r1[1] + r1[3]:
            # r1 and r2 intersects each other vertically
            overlap_h = r2[1] + r2[3] - r1[1]
        else:
            # r1 is included in r2 vertically
            overlap_h = r1[3]

    return overlap_w * overlap_h


def roi_comp(r1, r2):
    if not roi_check_overlap(r1, r2):
        return True
    size = roi_overlap_size(r1, r2)
    if r1[2] * r1[3] < r2[2] * r2[3]:
        # r1 < r2
        if float(size) / (r1[2] * r1[3]) < 0.25:
            return True
        if r2[2] * r2[3] > size * 2.25:
            return True
    else:
        # r1 > r2
        if float(size) / (r2[2] * r2[3]) < 0.25:
            return True
        if r1[2] * r1[3] > size * 2.25:
            return True
    return False
